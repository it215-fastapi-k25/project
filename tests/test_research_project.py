def test_3_1_create_project_auto_owner(client, register_and_login):
    owner = register_and_login("proj_owner1@test.com")
    r = client.post("/research-projects", json={"name": "AI Research"}, headers=owner["headers"])
    assert r.status_code == 201
    project_id = r.json()["data"]["id"]

    r2 = client.get(f"/research-projects/{project_id}/members", headers=owner["headers"])
    assert r2.status_code == 200
    assert len(r2.json()["data"]) == 1
    assert r2.json()["data"][0]["role"] == "OWNER"
    assert r2.json()["data"][0]["user_id"] == owner["user_id"]


def test_3_2_create_project_blank_name(client, register_and_login):
    owner = register_and_login("proj_owner2@test.com")
    r = client.post("/research-projects", json={"name": "   "}, headers=owner["headers"])
    assert r.status_code == 422


def test_3_3_list_only_my_projects(client, register_and_login, create_project):
    owner = register_and_login("proj_owner3@test.com")
    outsider = register_and_login("proj_outsider3@test.com")
    create_project(owner["headers"], "Owner's Project")

    r = client.get("/research-projects", headers=outsider["headers"])
    assert r.status_code == 200
    assert r.json()["data"] == []

    r2 = client.get("/research-projects", headers=owner["headers"])
    assert len(r2.json()["data"]) == 1


def test_3_4_search_projects(client, register_and_login, create_project):
    owner = register_and_login("proj_owner4@test.com")
    create_project(owner["headers"], "Machine Learning Study")
    create_project(owner["headers"], "Blockchain Research")

    r = client.get("/research-projects?search=machine", headers=owner["headers"])
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["name"] == "Machine Learning Study"


def test_3_5_member_can_view_detail(client, register_and_login, create_project):
    owner = register_and_login("proj_owner5@test.com")
    member = register_and_login("proj_member5@test.com")
    project_id = create_project(owner["headers"])
    client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])

    r = client.get(f"/research-projects/{project_id}", headers=member["headers"])
    assert r.status_code == 200


def test_3_6_outsider_cannot_view_detail(client, register_and_login, create_project):
    owner = register_and_login("proj_owner6@test.com")
    outsider = register_and_login("proj_outsider6@test.com")
    project_id = create_project(owner["headers"])

    r = client.get(f"/research-projects/{project_id}", headers=outsider["headers"])
    assert r.status_code == 403


def test_3_7_project_not_found(client, register_and_login):
    owner = register_and_login("proj_owner7@test.com")
    r = client.get("/research-projects/999999", headers=owner["headers"])
    assert r.status_code == 404


def test_3_8_owner_can_update(client, register_and_login, create_project):
    owner = register_and_login("proj_owner8@test.com")
    project_id = create_project(owner["headers"], "Old Name")
    r = client.patch(f"/research-projects/{project_id}", json={"name": "New Name"}, headers=owner["headers"])
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "New Name"


def test_3_9_member_cannot_update(client, register_and_login, create_project):
    owner = register_and_login("proj_owner9@test.com")
    member = register_and_login("proj_member9@test.com")
    project_id = create_project(owner["headers"])
    client.post(f"/research-projects/{project_id}/members", json={"user_id": member["user_id"]}, headers=owner["headers"])

    r = client.patch(f"/research-projects/{project_id}", json={"name": "Hacked"}, headers=member["headers"])
    assert r.status_code == 403


def test_3_10_owner_soft_delete(client, register_and_login, create_project):
    owner = register_and_login("proj_owner10@test.com")
    project_id = create_project(owner["headers"])
    r = client.delete(f"/research-projects/{project_id}", headers=owner["headers"])
    assert r.status_code == 204


def test_3_11_get_deleted_project_404(client, register_and_login, create_project):
    owner = register_and_login("proj_owner11@test.com")
    project_id = create_project(owner["headers"])
    client.delete(f"/research-projects/{project_id}", headers=owner["headers"])

    r = client.get(f"/research-projects/{project_id}", headers=owner["headers"])
    assert r.status_code == 404


def test_3_12_task_under_deleted_project_404(client, register_and_login, create_project):
    owner = register_and_login("proj_owner12@test.com")
    project_id = create_project(owner["headers"])
    r = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "Task X"}, headers=owner["headers"])
    task_id = r.json()["data"]["id"]

    client.delete(f"/research-projects/{project_id}", headers=owner["headers"])

    r2 = client.get(f"/research-tasks/{task_id}", headers=owner["headers"])
    assert r2.status_code == 404