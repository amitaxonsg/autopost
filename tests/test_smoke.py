import os

os.environ["FLASK_SECRET_KEY"] = "test-secret"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "test-password"
os.environ["SESSION_COOKIE_SECURE"] = "0"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["CREDENTIAL_ENCRYPTION_KEY"] = "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="

from app import app

def test_healthz():
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["app"] == "AutoPost"

def test_login_page_loads():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
    assert b"AutoPost" in response.data

def test_dashboard_redirects_when_logged_out():
    client = app.test_client()
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302)
    assert "/login" in response.headers["Location"]
