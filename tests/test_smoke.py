import os

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")
os.environ.setdefault("SESSION_COOKIE_SECURE", "0")

from app import app

def test_healthz():
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_login_page():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "AutoPost" in body
    assert "Developed by Axon 1Pro" in body
