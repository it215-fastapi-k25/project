import os
os.environ["DATABASE_URL"] = "sqlite:///./manual_check.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import io
from fastapi.testclient import TestClient
from app.db.database import Base, engine
from app import models
from app.main import app

if os.path.exists("manual_check.db"):
    os.remove("manual_check.db")
Base.metadata.create_all(bind=engine)

client = TestClient(app, raise_server_exceptions=False)
results = []


def check(case_id, desc, condition, extra=""):
    status_txt = "PASS" if condition else "FAIL"
    results.append((case_id, desc, status_txt, extra))
    print(f"[{status_txt}] {case_id} - {desc} {extra}")


def register_login(email, password="12345678", full_name="Test User"):
    client.post("/auth/register", json={"email": email, "full_name": full_name, "password": password})
    r = client.post("/auth/login", data={"username": email, "password": password})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/users/me", headers=headers).json()["data"]
    return {"headers": headers, "user_id": me["id"], "email": email}


def create_project(headers, name="Test Project"):
    r = client.post("/research-projects", json={"name": name}, headers=headers)
    return r.json()["data"]["id"]


def add_member(project_id, owner_headers, user_id):
    return client.post(f"/research-projects/{project_id}/members", json={"user_id": user_id}, headers=owner_headers)


# ---------- Group 5: Research Task ----------
owner = register_login("task_owner@test.com")
member = register_login("task_member@test.com")
outsider = register_login("task_outsider@test.com")
project_id = create_project(owner["headers"], "Task Test Project")
add_member(project_id, owner["headers"], member["user_id"])

# 5.1 Thanh vien tao hop le -> 201, status mac dinh TODO
r = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "Task A"}, headers=member["headers"])
task_a_id = r.json()["data"]["id"] if r.status_code == 201 else None
check("5.1", "Thanh vien tao task hop le", r.status_code == 201 and r.json()["data"]["status"] == "TODO", f"got {r.status_code}")

# 5.2 title toan khoang trang -> 422
r = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "   "}, headers=member["headers"])
check("5.2", "title toan khoang trang", r.status_code == 422, f"got {r.status_code}")

# 5.3 assignee_id la nguoi ngoai de tai -> 400
r = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "Task B", "assignee_id": outsider["user_id"]}, headers=member["headers"])
check("5.3", "assignee_id la nguoi ngoai de tai", r.status_code == 400, f"got {r.status_code}")

# 5.4 Nguoi ngoai de tai tao task -> 403
r = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "Task C"}, headers=outsider["headers"])
check("5.4", "Nguoi ngoai de tai tao task", r.status_code == 403, f"got {r.status_code}")

# seed data for filter/search/pagination
client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "Machine Learning Survey", "priority": "HIGH"}, headers=member["headers"])
client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "Data cleaning", "priority": "LOW"}, headers=member["headers"])
r_done = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "Write report"}, headers=member["headers"])
done_task_id = r_done.json()["data"]["id"]
# Chi OWNER hoac ASSIGNEE moi duoc sua task (permission matrix) -> dung owner de chuyen status
client.patch(f"/research-tasks/{done_task_id}", json={"status": "DONE"}, headers=owner["headers"])

# 5.5 Filter theo status
r = client.get(f"/research-projects/{project_id}/research-tasks?status=DONE", headers=member["headers"])
ok = r.status_code == 200 and all(t["status"] == "DONE" for t in r.json()["data"]["items"]) and len(r.json()["data"]["items"]) >= 1
check("5.5", "Filter theo status", ok, f"got {r.status_code}")

# 5.6 Ket hop nhieu dieu kien filter (status + priority)
r = client.get(f"/research-projects/{project_id}/research-tasks?status=TODO&priority=HIGH", headers=member["headers"])
ok = r.status_code == 200 and all(t["status"] == "TODO" and t["priority"] == "HIGH" for t in r.json()["data"]["items"])
check("5.6", "Ket hop nhieu dieu kien filter", ok, f"got {r.status_code}")

# 5.7 Search theo title, khong phan biet hoa thuong
r = client.get(f"/research-projects/{project_id}/research-tasks?search=machine", headers=member["headers"])
ok = r.status_code == 200 and any("Machine Learning Survey" == t["title"] for t in r.json()["data"]["items"])
check("5.7", "Search theo title khong phan biet hoa thuong", ok, f"got {r.status_code}")

# 5.8 Pagination
r = client.get(f"/research-projects/{project_id}/research-tasks?page=1&size=2", headers=member["headers"])
ok = r.status_code == 200 and len(r.json()["data"]["items"]) == 2 and r.json()["data"]["total"] >= 4
check("5.8", "Pagination dung so item va total", ok, f"got {r.status_code}, items={len(r.json()['data']['items']) if r.status_code==200 else '-'}, total={r.json()['data']['total'] if r.status_code==200 else '-'}")

# 5.9 Chi tiet task, la thanh vien de tai -> 200
r = client.get(f"/research-tasks/{task_a_id}", headers=member["headers"])
check("5.9", "Chi tiet task - la thanh vien", r.status_code == 200, f"got {r.status_code}")

# 5.10 Khong phai thanh vien de tai -> 403
r = client.get(f"/research-tasks/{task_a_id}", headers=outsider["headers"])
check("5.10", "Chi tiet task - khong phai thanh vien", r.status_code == 403, f"got {r.status_code}")

# 5.11 OWNER sua moi truong (bao gom status) -> 200
r = client.patch(f"/research-tasks/{task_a_id}", json={"status": "IN_PROGRESS", "priority": "HIGH"}, headers=owner["headers"])
check("5.11", "OWNER sua moi truong bao gom status", r.status_code == 200 and r.json()["data"]["status"] == "IN_PROGRESS", f"got {r.status_code}")

# 5.12 Assignee tu cap nhat status -> 200
r = client.patch(f"/research-tasks/{task_a_id}", json={"assignee_id": member["user_id"]}, headers=owner["headers"])
r2 = client.patch(f"/research-tasks/{task_a_id}", json={"status": "DONE"}, headers=member["headers"])
check("5.12", "Assignee tu cap nhat status", r2.status_code == 200, f"got {r2.status_code}")

# 5.13 Thanh vien khac (khong phai owner/assignee) sua -> 403
member2 = register_login("task_member2@test.com")
add_member(project_id, owner["headers"], member2["user_id"])
r = client.patch(f"/research-tasks/{task_a_id}", json={"status": "TODO"}, headers=member2["headers"])
check("5.13", "Thanh vien khac khong phai owner/assignee sua", r.status_code == 403, f"got {r.status_code}")

# 5.14 Go gan assignee_id = null -> 200, tra ve null
r = client.patch(f"/research-tasks/{task_a_id}", json={"assignee_id": None}, headers=owner["headers"])
check("5.14", "Go gan assignee_id = null", r.status_code == 200 and r.json()["data"]["assignee_id"] is None, f"got {r.status_code}, body={r.json()}")

# 5.15 OWNER hoac Assignee xoa -> 204
r_new = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "To delete"}, headers=member["headers"])
del_task_id = r_new.json()["data"]["id"]
r = client.delete(f"/research-tasks/{del_task_id}", headers=owner["headers"])
check("5.15", "OWNER hoac Assignee xoa task", r.status_code == 204, f"got {r.status_code}")

# 5.16 Khong phai owner/assignee xoa -> 403
r_new2 = client.post(f"/research-projects/{project_id}/research-tasks", json={"title": "To delete 2"}, headers=member["headers"])
del_task_id2 = r_new2.json()["data"]["id"]
r = client.delete(f"/research-tasks/{del_task_id2}", headers=member2["headers"])
check("5.16", "Khong phai owner/assignee xoa task", r.status_code == 403, f"got {r.status_code}")


# ---------- Group 6: Comment & Attachment ----------
# 6.1 Thanh vien binh luan -> 201
r = client.post(f"/research-tasks/{task_a_id}/comments", json={"content": "Nice work"}, headers=member["headers"])
check("6.1", "Thanh vien binh luan", r.status_code == 201, f"got {r.status_code}")

# 6.2 Nguoi ngoai de tai xem -> 403
r = client.get(f"/research-tasks/{task_a_id}/comments", headers=outsider["headers"])
check("6.2", "Nguoi ngoai de tai xem comment", r.status_code == 403, f"got {r.status_code}")

# 6.3 Upload file hop le -> 201
file_content = b"%PDF-1.4 fake pdf content"
r = client.post(
    f"/research-tasks/{task_a_id}/attachments",
    files={"file": ("report.pdf", io.BytesIO(file_content), "application/pdf")},
    headers=member["headers"],
)
check("6.3", "Upload file hop le", r.status_code == 201, f"got {r.status_code}")

# 6.4 Upload file sai dinh dang -> 400
r = client.post(
    f"/research-tasks/{task_a_id}/attachments",
    files={"file": ("malware.exe", io.BytesIO(b"MZ..."), "application/x-msdownload")},
    headers=member["headers"],
)
check("6.4", "Upload file sai dinh dang", r.status_code == 400, f"got {r.status_code}")

# 6.5 Upload file vuot dung luong cho phep -> 400 (hoac 413)
big_content = b"0" * (10 * 1024 * 1024 + 100)
r = client.post(
    f"/research-tasks/{task_a_id}/attachments",
    files={"file": ("big.pdf", io.BytesIO(big_content), "application/pdf")},
    headers=member["headers"],
)
check("6.5", "Upload file vuot dung luong cho phep", r.status_code in (400, 413), f"got {r.status_code}")

print("\n\n=== SUMMARY ===")
passed = sum(1 for _, _, s, _ in results if s == "PASS")
print(f"{passed}/{len(results)} PASS")
for c in results:
    if c[2] != "PASS":
        print("FAILED:", c)
