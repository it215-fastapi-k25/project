def test_register_success(client):
    r = client.post("/auth/register", json={"email": "a@test.com", "full_name": "A", "password": "12345678"})
    assert r.status_code == 200
    assert "password" not in r.json()
    assert "password_hash" not in r.json()


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@test.com", "full_name": "A", "password": "12345678"})
    r = client.post("/auth/register", json={"email": "dup@test.com", "full_name": "B", "password": "12345678"})
    assert r.status_code == 409


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "b@test.com", "full_name": "B", "password": "12345678"})
    r = client.post("/auth/login", data={"username": "b@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_protected_endpoint_without_token(client):
    r = client.get("/users/me")
    assert r.status_code == 401


def test_protected_endpoint_with_token(client, register_and_login):
    headers = register_and_login("c@test.com")
    r = client.get("/users/me", headers=headers)
    assert r.status_code == 200