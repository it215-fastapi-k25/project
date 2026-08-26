import time


def test_1_1_register_success(client):
    r = client.post("/auth/register", json={"email": "u1@test.com", "full_name": "User One", "password": "12345678"})
    assert r.status_code == 200
    body = r.json()
    assert "password" not in body
    assert "password_hash" not in body
    assert body["email"] == "u1@test.com"


def test_1_2_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@test.com", "full_name": "A", "password": "12345678"})
    r = client.post("/auth/register", json={"email": "dup@test.com", "full_name": "B", "password": "12345678"})
    assert r.status_code == 409


def test_1_3_register_invalid_email(client):
    r = client.post("/auth/register", json={"email": "not-an-email", "full_name": "A", "password": "12345678"})
    assert r.status_code == 422


def test_1_4_register_short_password(client):
    r = client.post("/auth/register", json={"email": "shortpass@test.com", "full_name": "A", "password": "123"})
    assert r.status_code == 422


def test_1_5_register_blank_full_name(client):
    r = client.post("/auth/register", json={"email": "blankname@test.com", "full_name": "   ", "password": "12345678"})
    assert r.status_code == 422


def test_1_6_register_cannot_escalate_role(client):
    r = client.post("/auth/register", json={
        "email": "hacker@test.com", "full_name": "Hacker", "password": "12345678", "role": "ADMIN"
    })
    assert r.status_code == 200
    assert r.json()["role"] == "USER"


def test_1_7_login_success(client):
    client.post("/auth/register", json={"email": "login1@test.com", "full_name": "A", "password": "12345678"})
    r = client.post("/auth/login", data={"username": "login1@test.com", "password": "12345678"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert "refresh_token" in r.json()


def test_1_8_login_wrong_password(client):
    client.post("/auth/register", json={"email": "login2@test.com", "full_name": "A", "password": "12345678"})
    r = client.post("/auth/login", data={"username": "login2@test.com", "password": "wrongpass"})
    assert r.status_code == 401
    msg_wrong_pass = r.json()["message"] if "message" in r.json() else r.json().get("detail")

    r2 = client.post("/auth/login", data={"username": "khong-ton-tai@test.com", "password": "wrongpass"})
    assert r2.status_code == 401
    msg_no_user = r2.json()["message"] if "message" in r2.json() else r2.json().get("detail")

    assert msg_wrong_pass == msg_no_user


def test_1_9_login_inactive_account(client, register_and_login, make_inactive):
    user = register_and_login("inactive@test.com")
    make_inactive("inactive@test.com")
    r = client.post("/auth/login", data={"username": "inactive@test.com", "password": "12345678"})
    assert r.status_code == 401


def test_1_10_rate_limit_login(client):
    client.post("/auth/register", json={"email": "ratelimit@test.com", "full_name": "A", "password": "12345678"})
    statuses = []
    for _ in range(7):
        r = client.post("/auth/login", data={"username": "ratelimit@test.com", "password": "wrongpass"})
        statuses.append(r.status_code)
    assert 429 in statuses
    assert statuses[:5] == [401, 401, 401, 401, 401]


def test_1_11_refresh_valid(client, register_and_login):
    user = register_and_login("refresh1@test.com")
    r = client.post("/auth/refresh", json={"refresh_token": user["refresh_token"]})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_1_12_refresh_using_access_token(client, register_and_login):
    user = register_and_login("refresh2@test.com")
    r = client.post("/auth/refresh", json={"refresh_token": user["token"]})
    assert r.status_code == 401


def test_1_13_refresh_garbage_token(client):
    r = client.post("/auth/refresh", json={"refresh_token": "garbage-token-xyz"})
    assert r.status_code == 401