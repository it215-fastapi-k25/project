def test_2_1_get_me_with_token(client, register_and_login):
    user = register_and_login("me1@test.com", full_name="Me One")
    r = client.get("/users/me", headers=user["headers"])
    assert r.status_code == 200
    body = r.json()["data"]
    assert body["email"] == "me1@test.com"
    assert "password_hash" not in body


def test_2_2_get_me_without_token(client):
    r = client.get("/users/me")
    assert r.status_code == 401


def test_2_3_list_users_as_admin(client, register_and_login, make_admin):
    admin = register_and_login("admin1@test.com")
    make_admin("admin1@test.com")
    admin["headers"]  # header van dung token cu, role da doi trong DB nen get_current_user doc lai dung
    r = client.get("/users", headers=admin["headers"])
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


def test_2_4_list_users_as_regular_user(client, register_and_login):
    user = register_and_login("regular1@test.com")
    r = client.get("/users", headers=user["headers"])
    assert r.status_code == 403


def test_2_5_search_users(client, register_and_login, make_admin):
    admin = register_and_login("admin2@test.com")
    make_admin("admin2@test.com")
    register_and_login("nguyen.van.a@test.com", full_name="Nguyen Van A")
    register_and_login("tran.thi.b@test.com", full_name="Tran Thi B")

    r = client.get("/users?search=nguyen", headers=admin["headers"])
    assert r.status_code == 200
    emails = [u["email"] for u in r.json()["data"]]
    assert "nguyen.van.a@test.com" in emails
    assert "tran.thi.b@test.com" not in emails
