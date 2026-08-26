def test_4_1_owner_add_member(client, register_and_login, create_project):
    owner = register_and_login("mem_owner1@test.com")
    member = register_and_login("mem_target1@test.com")
    project_id = create_project(owner["headers"])

    r = client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])
    assert r.status_code == 201
    assert r.json()["data"]["role"] == "MEMBER"


def test_4_2_add_duplicate_member(client, register_and_login, create_project):
    owner = register_and_login("mem_owner2@test.com")
    member = register_and_login("mem_target2@test.com")
    project_id = create_project(owner["headers"])
    client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])

    r = client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])
    assert r.status_code == 409


def test_4_3_add_member_invalid_user_id(client, register_and_login, create_project):
    owner = register_and_login("mem_owner3@test.com")
    project_id = create_project(owner["headers"])

    r = client.post(f"/research-projects/{project_id}/members", json={"user_id": 0}, headers=owner["headers"])
    assert r.status_code == 422

    r2 = client.post(f"/research-projects/{project_id}/members", json={"user_id": -5}, headers=owner["headers"])
    assert r2.status_code == 422


def test_4_4_add_member_nonexistent_user(client, register_and_login, create_project):
    owner = register_and_login("mem_owner4@test.com")
    project_id = create_project(owner["headers"])

    r = client.post(f"/research-projects/{project_id}/members", json={"user_id": 999999}, headers=owner["headers"])
    assert r.status_code == 404


def test_4_5_non_owner_cannot_add_member(client, register_and_login, create_project):
    owner = register_and_login("mem_owner5@test.com")
    member = register_and_login("mem_member5@test.com")
    outsider_target = register_and_login("mem_target5@test.com")
    project_id = create_project(owner["headers"])
    client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])

    r = client.post(f"/research-projects/{project_id}/members", json={"user_id": outsider_target["user_id"]}, headers=member["headers"])
    assert r.status_code == 403


def test_4_6_list_members(client, register_and_login, create_project):
    owner = register_and_login("mem_owner6@test.com")
    member = register_and_login("mem_target6@test.com")
    project_id = create_project(owner["headers"])
    client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])

    r = client.get(f"/research-projects/{project_id}/members", headers=member["headers"])
    assert r.status_code == 200
    roles = {m["user_id"]: m["role"] for m in r.json()["data"]}
    assert roles[owner["user_id"]] == "OWNER"
    assert roles[member["user_id"]] == "MEMBER"


def test_4_7_remove_regular_member(client, register_and_login, create_project):
    owner = register_and_login("mem_owner7@test.com")
    member = register_and_login("mem_target7@test.com")
    project_id = create_project(owner["headers"])
    client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])

    r = client.delete(f"/research-projects/{project_id}/members/{member['user_id']}", headers=owner["headers"])
    assert r.status_code == 204


def test_4_8_cannot_remove_last_owner(client, register_and_login, create_project):
    owner = register_and_login("mem_owner8@test.com")
    project_id = create_project(owner["headers"])

    r = client.delete(f"/research-projects/{project_id}/members/{owner['user_id']}", headers=owner["headers"])
    assert r.status_code == 400