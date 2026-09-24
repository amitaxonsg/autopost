import hmac
import re
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash

from config import Config
from models import ActivityLog, Setting, Topic, db
from security_utils import decrypt_value, encrypt_value
from services.openai_service import generate_article, generate_image_bytes, test_openai
from services.wordpress_service import create_post, test_connection, update_post_status, upload_media

csrf = CSRFProtect()
SECRET_SETTING_KEYS = {"openai_api_key", "wordpress_app_password"}

DEFAULT_SETTINGS = {
    "wordpress_url": "",
    "wordpress_username": "",
    "wordpress_app_password": "",
    "openai_api_key": "",
    "openai_model": "",
    "image_model": "",
    "publishing_mode": "draft",
    "automation_enabled": "1",
    "frequency_mode": "weekly",
    "posts_per_week": "2",
    "posts_per_month": "8",
    "preferred_time": "10:00",
    "timezone": "Asia/Singapore",
    "generate_image": "1",
    "seo_enabled": "1",
    "last_auto_run": "",
}

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()
        _seed_defaults(app)

    register_routes(app)
    return app

def _seed_defaults(app):
    defaults = dict(DEFAULT_SETTINGS)
    defaults["openai_model"] = app.config["DEFAULT_OPENAI_MODEL"]
    defaults["image_model"] = app.config["DEFAULT_IMAGE_MODEL"]
    defaults["posts_per_week"] = str(app.config["DEFAULT_POSTS_PER_WEEK"])
    defaults["timezone"] = app.config["DEFAULT_TIMEZONE"]
    for key, value in defaults.items():
        if Setting.query.filter_by(key=key).first() is None:
            row = Setting(key=key, value="", secret=key in SECRET_SETTING_KEYS)
            db.session.add(row)
            db.session.flush()
            if value:
                set_setting(key, value, commit=False)
    db.session.commit()

def logged_in():
    return bool(session.get("logged_in"))

def require_login():
    if not logged_in():
        return redirect(url_for("login"))
    return None

def verify_admin_password(app, supplied):
    stored_hash = app.config.get("ADMIN_PASSWORD_HASH") or ""
    if stored_hash:
        return check_password_hash(stored_hash, supplied)
    expected = app.config.get("ADMIN_PASSWORD") or ""
    return hmac.compare_digest(str(supplied), str(expected))

def get_setting(key, default=""):
    row = Setting.query.filter_by(key=key).first()
    if not row or not row.value:
        return default
    if row.secret:
        return decrypt_value(row.value, Config.CREDENTIAL_ENCRYPTION_KEY)
    return row.value

def set_setting(key, value, commit=True):
    row = Setting.query.filter_by(key=key).first()
    if not row:
        row = Setting(key=key, secret=key in SECRET_SETTING_KEYS)
        db.session.add(row)
    if row.secret:
        row.value = encrypt_value(value, Config.CREDENTIAL_ENCRYPTION_KEY) if value else ""
    else:
        row.value = value or ""
    if commit:
        db.session.commit()

def log_event(event, detail="", level="info"):
    db.session.add(ActivityLog(event=event, detail=detail, level=level))
    db.session.commit()

def read_memory(app):
    p = Path(app.config["CLIENT_MEMORY_PATH"])
    return p.read_text(encoding="utf-8") if p.exists() else ""

def write_memory(app, text):
    p = Path(app.config["CLIENT_MEMORY_PATH"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def credentials_ready():
    return bool(
        get_setting("wordpress_url")
        and get_setting("wordpress_username")
        and get_setting("wordpress_app_password")
        and get_setting("openai_api_key")
        and get_setting("openai_model")
    )

def process_topic(topic_id):
    topic = db.session.get(Topic, topic_id)
    if not topic:
        raise RuntimeError("Topic not found.")
    if not topic.enabled:
        raise RuntimeError("Topic is disabled.")
    if not credentials_ready():
        raise RuntimeError("OpenAI and WordPress connections must be configured first.")

    topic.status = "generating"
    topic.attempts = (topic.attempts or 0) + 1
    topic.last_error = ""
    db.session.commit()

    try:
        article = generate_article(
            get_setting("openai_api_key"),
            get_setting("openai_model", Config.DEFAULT_OPENAI_MODEL),
            topic,
            read_memory(_app_ref()),
        )

        media_id = None
        if get_setting("generate_image", "1") == "1":
            image_bytes, mime = generate_image_bytes(
                get_setting("openai_api_key"),
                get_setting("image_model", Config.DEFAULT_IMAGE_MODEL),
                article["image_prompt"],
            )
            safe = re.sub(r"[^a-z0-9]+", "-", article["title"].lower()).strip("-")[:70] or "autopost-image"
            ext = "jpg" if "jpeg" in mime else "png"
            media_id = upload_media(
                get_setting("wordpress_url"),
                get_setting("wordpress_username"),
                get_setting("wordpress_app_password"),
                image_bytes,
                f"{safe}.{ext}",
                mime,
                article.get("image_alt", ""),
            )

        publish_mode = get_setting("publishing_mode", "draft")
        wp_status = "publish" if publish_mode == "auto_publish" else "draft"
        result = create_post(
            get_setting("wordpress_url"),
            get_setting("wordpress_username"),
            get_setting("wordpress_app_password"),
            article,
            status=wp_status,
            featured_media_id=media_id,
        )

        topic.wordpress_post_id = result.get("id")
        topic.wordpress_url = result.get("link", "")
        topic.generated_title = article.get("title", "")
        topic.status = "published" if wp_status == "publish" else "draft_created"
        db.session.commit()
        log_event("Post created", f"{topic.title} -> {topic.status}")
        return topic
    except Exception as exc:
        topic.status = "failed"
        topic.last_error = str(exc)
        db.session.commit()
        log_event("Generation failed", f"{topic.title}: {exc}", "error")
        raise

_APP = None

def _app_ref():
    global _APP
    if _APP is None:
        from flask import current_app
        return current_app
    return _APP

def schedule_due():
    if get_setting("automation_enabled", "1") != "1":
        return None
    mode = get_setting("frequency_mode", "weekly")
    if mode == "manual":
        return None

    now = datetime.utcnow()
    explicit = Topic.query.filter(
        Topic.enabled.is_(True),
        Topic.status.in_(["ready", "scheduled"]),
        Topic.scheduled_at.isnot(None),
        Topic.scheduled_at <= now,
    ).order_by(Topic.scheduled_at.asc()).first()
    if explicit:
        return explicit

    last_text = get_setting("last_auto_run", "")
    last_run = None
    if last_text:
        try:
            last_run = datetime.fromisoformat(last_text)
        except ValueError:
            pass

    if mode == "monthly":
        count = max(1, int(get_setting("posts_per_month", "8")))
        interval = timedelta(days=30 / count)
    else:
        count = max(1, int(get_setting("posts_per_week", "2")))
        interval = timedelta(days=7 / count)

    if last_run and now < last_run + interval:
        return None

    return Topic.query.filter(
        Topic.enabled.is_(True),
        Topic.status == "ready",
        Topic.scheduled_at.is_(None),
    ).order_by(Topic.created_at.asc()).first()

def process_due_once(app):
    with app.app_context():
        topic = schedule_due()
        if not topic:
            return False
        process_topic(topic.id)
        set_setting("last_auto_run", datetime.utcnow().isoformat(timespec="seconds"))
        return True

def register_routes(app):
    global _APP
    _APP = app

    @app.context_processor
    def inject_brand():
        return {
            "brand_name": app.config["BRAND_NAME"],
            "brand_byline": app.config["BRAND_BYLINE"],
            "brand_url": app.config["BRAND_URL"],
            "support_email": app.config["SUPPORT_EMAIL"],
        }

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "app": "AutoPost"}, 200

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if logged_in():
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            email_ok = hmac.compare_digest(
                request.form.get("email", "").strip().lower(),
                app.config["ADMIN_EMAIL"].strip().lower(),
            )
            password_ok = verify_admin_password(app, request.form.get("password", ""))
            if email_ok and password_ok:
                session.clear()
                session["logged_in"] = True
                session.permanent = True
                log_event("Login", "Administrator logged in.")
                return redirect(url_for("dashboard"))
            flash("Incorrect email or password.", "error")
        return render_template("login.html")

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    def dashboard():
        gate = require_login()
        if gate:
            return gate
        counts = {
            "ready": Topic.query.filter_by(enabled=True, status="ready").count(),
            "scheduled": Topic.query.filter(Topic.enabled.is_(True), Topic.scheduled_at.isnot(None), Topic.status.in_(["ready", "scheduled"])).count(),
            "drafts": Topic.query.filter_by(status="draft_created").count(),
            "failed": Topic.query.filter_by(status="failed").count(),
        }
        next_topic = Topic.query.filter(
            Topic.enabled.is_(True),
            Topic.status.in_(["ready", "scheduled"]),
        ).order_by(Topic.scheduled_at.asc().nullslast(), Topic.created_at.asc()).first()
        recent = Topic.query.order_by(Topic.updated_at.desc()).limit(8).all()
        logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(8).all()
        return render_template(
            "dashboard.html",
            counts=counts,
            next_topic=next_topic,
            recent=recent,
            logs=logs,
            wp_ready=bool(get_setting("wordpress_url") and get_setting("wordpress_app_password")),
            ai_ready=bool(get_setting("openai_api_key")),
            automation=get_setting("automation_enabled", "1") == "1",
            publishing_mode=get_setting("publishing_mode", "draft"),
            frequency_mode=get_setting("frequency_mode", "weekly"),
        )

    @app.route("/topics", methods=["GET", "POST"])
    def topics():
        gate = require_login()
        if gate:
            return gate
        if request.method == "POST":
            scheduled = request.form.get("scheduled_at", "").strip()
            row = Topic(
                title=request.form.get("title", "").strip(),
                keywords=request.form.get("keywords", "").strip(),
                category=request.form.get("category", "").strip(),
                notes=request.form.get("notes", "").strip(),
                scheduled_at=datetime.fromisoformat(scheduled) if scheduled else None,
                status="scheduled" if scheduled else "ready",
            )
            if not row.title:
                flash("Topic is required.", "error")
            else:
                db.session.add(row)
                db.session.commit()
                log_event("Topic added", row.title)
                flash("Topic added to the queue.", "success")
            return redirect(url_for("topics"))
        status = request.args.get("status", "all")
        q = Topic.query
        if status == "disabled":
            q = q.filter_by(enabled=False)
        elif status != "all":
            q = q.filter_by(status=status)
        rows = q.order_by(Topic.scheduled_at.asc().nullslast(), Topic.created_at.desc()).all()
        return render_template("topics.html", topics=rows, current_status=status)

    @app.route("/topics/<int:topic_id>/edit", methods=["GET", "POST"])
    def edit_topic(topic_id):
        gate = require_login()
        if gate:
            return gate
        topic = db.get_or_404(Topic, topic_id)
        if request.method == "POST":
            topic.title = request.form.get("title", "").strip()
            topic.keywords = request.form.get("keywords", "").strip()
            topic.category = request.form.get("category", "").strip()
            topic.notes = request.form.get("notes", "").strip()
            scheduled = request.form.get("scheduled_at", "").strip()
            topic.scheduled_at = datetime.fromisoformat(scheduled) if scheduled else None
            if topic.status in ["ready", "scheduled"]:
                topic.status = "scheduled" if scheduled else "ready"
            db.session.commit()
            log_event("Topic updated", topic.title)
            flash("Topic updated.", "success")
            return redirect(url_for("topics"))
        return render_template("topic_edit.html", topic=topic)

    @app.post("/topics/<int:topic_id>/toggle")
    def toggle_topic(topic_id):
        gate = require_login()
        if gate:
            return gate
        topic = db.get_or_404(Topic, topic_id)
        topic.enabled = not topic.enabled
        db.session.commit()
        log_event("Topic toggled", f"{topic.title}: enabled={topic.enabled}")
        return redirect(request.referrer or url_for("topics"))

    @app.post("/topics/<int:topic_id>/delete")
    def delete_topic(topic_id):
        gate = require_login()
        if gate:
            return gate
        topic = db.get_or_404(Topic, topic_id)
        name = topic.title
        db.session.delete(topic)
        db.session.commit()
        log_event("Topic deleted", name)
        flash("Topic deleted.", "success")
        return redirect(url_for("topics"))

    @app.post("/topics/<int:topic_id>/generate")
    def generate_now(topic_id):
        gate = require_login()
        if gate:
            return gate
        try:
            process_topic(topic_id)
            flash("Article created successfully.", "success")
        except Exception as exc:
            flash(f"Generation failed: {exc}", "error")
        return redirect(url_for("topics"))

    @app.post("/topics/<int:topic_id>/retry")
    def retry_topic(topic_id):
        gate = require_login()
        if gate:
            return gate
        topic = db.get_or_404(Topic, topic_id)
        topic.status = "ready"
        topic.last_error = ""
        db.session.commit()
        flash("Topic returned to the ready queue.", "success")
        return redirect(url_for("topics"))

    @app.post("/topics/<int:topic_id>/publish")
    def publish_topic(topic_id):
        gate = require_login()
        if gate:
            return gate
        topic = db.get_or_404(Topic, topic_id)
        if not topic.wordpress_post_id:
            flash("This topic does not have a WordPress draft yet.", "error")
            return redirect(url_for("topics"))
        try:
            result = update_post_status(
                get_setting("wordpress_url"),
                get_setting("wordpress_username"),
                get_setting("wordpress_app_password"),
                topic.wordpress_post_id,
                "publish",
            )
            topic.status = "published"
            topic.wordpress_url = result.get("link", topic.wordpress_url)
            db.session.commit()
            log_event("Post published", topic.title)
            flash("WordPress post published.", "success")
        except Exception as exc:
            flash(f"Publish failed: {exc}", "error")
        return redirect(url_for("topics"))

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        gate = require_login()
        if gate:
            return gate
        normal_keys = [
            "wordpress_url", "wordpress_username", "openai_model", "image_model",
            "publishing_mode", "frequency_mode", "posts_per_week", "posts_per_month",
            "preferred_time", "timezone",
        ]
        toggles = ["automation_enabled", "generate_image", "seo_enabled"]
        if request.method == "POST":
            for key in normal_keys:
                set_setting(key, request.form.get(key, "").strip(), commit=False)
            for key in toggles:
                set_setting(key, "1" if request.form.get(key) == "1" else "0", commit=False)
            if request.form.get("openai_api_key", "").strip():
                set_setting("openai_api_key", request.form["openai_api_key"].strip(), commit=False)
            if request.form.get("wordpress_app_password", "").strip():
                set_setting("wordpress_app_password", request.form["wordpress_app_password"].strip(), commit=False)
            db.session.commit()
            log_event("Settings updated")
            flash("Settings saved.", "success")
            return redirect(url_for("settings"))

        data = {k: get_setting(k, DEFAULT_SETTINGS.get(k, "")) for k in normal_keys + toggles}
        data["has_openai_key"] = bool(get_setting("openai_api_key"))
        data["has_wp_password"] = bool(get_setting("wordpress_app_password"))
        return render_template("settings.html", settings=data)

    @app.post("/settings/test-wordpress")
    def test_wordpress_route():
        gate = require_login()
        if gate:
            return gate
        ok, message = test_connection(
            get_setting("wordpress_url"),
            get_setting("wordpress_username"),
            get_setting("wordpress_app_password"),
        )
        flash(message, "success" if ok else "error")
        return redirect(url_for("settings"))

    @app.post("/settings/test-openai")
    def test_openai_route():
        gate = require_login()
        if gate:
            return gate
        ok, message = test_openai(
            get_setting("openai_api_key"),
            get_setting("openai_model", app.config["DEFAULT_OPENAI_MODEL"]),
        )
        flash(message, "success" if ok else "error")
        return redirect(url_for("settings"))

    @app.route("/memory", methods=["GET", "POST"])
    def memory():
        gate = require_login()
        if gate:
            return gate
        if request.method == "POST":
            write_memory(app, request.form.get("memory", ""))
            log_event("Memory updated")
            flash("Brand memory saved.", "success")
            return redirect(url_for("memory"))
        return render_template("memory.html", memory=read_memory(app))

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
