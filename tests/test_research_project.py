def test_create_project_auto_owner(client, register_and_login):
    headers = register_and_login("owner1@test.com")
    r = client.post("/research-projects", json={"name": "AI Research"}, headers=headers)
    assert r.status_code == 201
    project_id = r.json()["id"]
    r = client.get(f"/research-projects/{project_id}/members", headers=headers)
    assert len(r.json()) == 1
    assert r.json()[0]["role"] == "OWNER"


def test_outsider_cannot_view_project(client, register_and_login):
    owner_headers = register_and_login("owner2@test.com")
    outsider_headers = register_and_login("outsider2@test.com")
    r = client.post("/research-projects", json={"name": "Private Project"}, headers=owner_headers)
    project_id = r.json()["id"]
    r = client.get(f"/research-projects/{project_id}", headers=outsider_headers)
    assert r.status_code == 403


def test_blank_project_name_rejected(client, register_and_login):
    headers = register_and_login("owner3@test.com")
    r = client.post("/research-projects", json={"name": "   "}, headers=headers)
    assert r.status_code == 422


def test_cannot_remove_last_owner(client, register_and_login):
    headers = register_and_login("owner4@test.com")
    r = client.post("/research-projects", json={"name": "Solo Project"}, headers=headers)
    project_id = r.json()["id"]
    r = client.delete(f"/research-projects/{project_id}/members/1", headers=headers)
    assert r.status_code == 400