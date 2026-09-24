from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    keywords = db.Column(db.String(600), default="")
    category = db.Column(db.String(120), default="")
    notes = db.Column(db.Text, default="")
    scheduled_at = db.Column(db.DateTime, nullable=True, index=True)
    enabled = db.Column(db.Boolean, default=True, index=True)
    status = db.Column(db.String(40), default="ready", index=True)
    wordpress_post_id = db.Column(db.Integer, nullable=True)
    wordpress_url = db.Column(db.String(600), default="")
    generated_title = db.Column(db.String(300), default="")
    last_error = db.Column(db.Text, default="")
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, default="")
    secret = db.Column(db.Boolean, default=False)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(160), nullable=False)
    detail = db.Column(db.Text, default="")
    level = db.Column(db.String(20), default="info")
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
