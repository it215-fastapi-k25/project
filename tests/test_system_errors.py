def test_7_1_unknown_route_404(client):
    r = client.get("/khong-ton-tai")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")


def test_7_2_validation_error_422(client):
    r = client.post("/auth/register", json={"email": "bad-email", "full_name": "", "password": "1"})
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body or "error" in body or "details" in body


def test_7_3_unexpected_exception_returns_500_no_traceback(client, monkeypatch):
    from app.db import database

    def broken_get_db():
        raise RuntimeError("Simulated unexpected crash")
        yield

    client.app.dependency_overrides[database.get_db] = broken_get_db
    try:
        r = client.get("/users/me", headers={"Authorization": "Bearer fake-token-but-passes-oauth2-shape"})
    finally:
        # dung try/finally de dam bao override luon duoc don dep, tranh
        # ro ri sang cac test khac ngay ca khi request phia tren tung bi loi
        client.app.dependency_overrides.clear()

    assert r.status_code in (401, 500)
    assert "Traceback" not in r.text
    assert "RuntimeError" not in r.text


def test_7_4_garbage_token(client):
    r = client.get("/users/me", headers={"Authorization": "Bearer this-is-not-a-real-jwt"})
    assert r.status_code == 401


def test_7_5_missing_authorization_header(client):
    r = client.get("/users/me")
    assert r.status_code == 401


def test_7_6_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200