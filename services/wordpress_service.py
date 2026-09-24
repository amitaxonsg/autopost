import re
import requests
from requests.auth import HTTPBasicAuth

def _base(url: str) -> str:
    return (url or "").rstrip("/")

def _auth(username: str, app_password: str):
    return HTTPBasicAuth(username, app_password)

def test_connection(url: str, username: str, app_password: str) -> tuple[bool, str]:
    if not all([url, username, app_password]):
        return False, "WordPress URL, username and Application Password are required."
    try:
        r = requests.get(f"{_base(url)}/wp-json/wp/v2/users/me", auth=_auth(username, app_password), timeout=20)
        if r.ok:
            data = r.json()
            return True, f"Connected as {data.get('name') or data.get('slug') or username}."
        return False, f"WordPress returned HTTP {r.status_code}: {r.text[:200]}"
    except Exception as exc:
        return False, str(exc)

def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\\s-]", "", value or "").strip().lower()
    return re.sub(r"[\\s_-]+", "-", value)

def ensure_term(url, username, app_password, taxonomy: str, name: str):
    if not name:
        return None
    endpoint = f"{_base(url)}/wp-json/wp/v2/{taxonomy}"
    r = requests.get(endpoint, params={"search": name, "per_page": 20}, auth=_auth(username, app_password), timeout=20)
    r.raise_for_status()
    for item in r.json():
        if item.get("name", "").casefold() == name.casefold():
            return item["id"]
    r = requests.post(endpoint, json={"name": name, "slug": _slug(name)}, auth=_auth(username, app_password), timeout=20)
    if r.status_code == 400:
        try:
            term_id = r.json().get("data", {}).get("term_id")
            if term_id:
                return term_id
        except Exception:
            pass
    r.raise_for_status()
    return r.json()["id"]

def upload_media(url, username, app_password, image_bytes: bytes, filename: str, mime_type: str, alt_text: str = "") -> int:
    endpoint = f"{_base(url)}/wp-json/wp/v2/media"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"', "Content-Type": mime_type}
    r = requests.post(endpoint, data=image_bytes, headers=headers, auth=_auth(username, app_password), timeout=90)
    r.raise_for_status()
    media_id = r.json()["id"]
    if alt_text:
        requests.post(f"{endpoint}/{media_id}", json={"alt_text": alt_text}, auth=_auth(username, app_password), timeout=20).raise_for_status()
    return media_id

def create_post(url, username, app_password, article: dict, status: str = "draft", featured_media_id=None) -> dict:
    category_ids = []
    if article.get("category"):
        cid = ensure_term(url, username, app_password, "categories", article["category"])
        if cid:
            category_ids.append(cid)

    tag_ids = []
    for tag in article.get("tags", [])[:10]:
        tid = ensure_term(url, username, app_password, "tags", str(tag))
        if tid:
            tag_ids.append(tid)

    payload = {
        "title": article["title"],
        "content": article["content_html"],
        "excerpt": article.get("excerpt", ""),
        "status": status,
        "categories": category_ids,
        "tags": tag_ids,
    }
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    r = requests.post(f"{_base(url)}/wp-json/wp/v2/posts", json=payload, auth=_auth(username, app_password), timeout=60)
    r.raise_for_status()
    return r.json()

def update_post_status(url, username, app_password, post_id: int, status: str) -> dict:
    r = requests.post(f"{_base(url)}/wp-json/wp/v2/posts/{post_id}", json={"status": status}, auth=_auth(username, app_password), timeout=30)
    r.raise_for_status()
    return r.json()
