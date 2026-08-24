# Research Group Management API

## Giới thiệu

API quản lý nhóm nghiên cứu, xây dựng bằng FastAPI + SQLAlchemy + MySQL.
Các chức năng chính: quản lý User, ResearchProject, ResearchMember, ResearchTask.

## Yêu cầu hệ thống

- Python 3.10 trở lên
- MySQL 8.0 trở lên
- pip

## Cài đặt môi trường

Tạo virtual environment:

```bash
python -m venv venv
```

Kích hoạt venv:

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Cài dependency:

```bash
pip install -r requirements.txt
```

## Cấu hình biến môi trường

Copy file mẫu và chỉnh sửa:

```bash
cp .env.example .env
```

Các biến cần cấu hình trong `.env`:

| Biến | Mô tả | Ví dụ |
|---|---|---|
| DATABASE_URL | Chuỗi kết nối MySQL | mysql+pymysql://root:pass@localhost:3306/research_management_db |
| SECRET_KEY | Khóa bí mật dùng ký JWT | chuỗi ngẫu nhiên dài |
| ALGORITHM | Thuật toán mã hóa JWT | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Thời gian sống của access token | 30 |
| ENVIRONMENT | Môi trường chạy | development hoặc production |
| CORS_ORIGINS | Danh sách domain được phép gọi API | ["http://localhost:3000"] |

## Khởi tạo database

Tạo database rỗng trong MySQL trước:

```sql
CREATE DATABASE research_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Tạo bảng từ model:

```bash
python -m app.db.init_db
```

## Seed dữ liệu mẫu (tùy chọn)

```bash
python -m scripts.seed
```

Tài khoản mẫu sau khi seed:

| Email | Mật khẩu | Vai trò |
|---|---|---|
| admin@research-demo.com| Admin@12345 | ADMIN |
| owner@research-demo.com | Owner@12345 | USER (owner của project mẫu) |
| member@research-demo.com | Member@12345 | USER (member của project mẫu) |

## Chạy ứng dụng

```bash
uvicorn app.main:app --reload
```

Ứng dụng chạy tại: http://127.0.0.1:8000

Kiểm tra sức khỏe hệ thống: http://127.0.0.1:8000/health

Swagger UI (tài liệu API tương tác): http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc

## Cấu trúc thư mục

research_management/
├── app/
│ ├── core/ cấu hình, security, exception
│ │ ├── config.py
│ │ ├── security.py
│ │ └── exceptions.py
│ ├── db/ kết nối và khởi tạo database
│ │ ├── database.py
│ │ └── init_db.py
│ ├── models/ SQLAlchemy models
│ │ ├── user.py
│ │ ├── research_project.py
│ │ └── research_task.py
│ ├── schemas/ Pydantic schemas
│ │ ├── user.py
│ │ ├── research_project.py
│ │ └── research_task.py
│ ├── routers/ FastAPI routers (Tiết 2)
│ ├── services/ logic nghiệp vụ (Tiết 2)
│ ├── dependencies/ dependency dùng chung (Tiết 2)
│ ├── utils/ hàm tiện ích
│ └── main.py entry point
├── scripts/
│ └── seed.py seed dữ liệu mẫu
├── tests/ unit/integration test
├── .env.example
├── requirements.txt
└── README.md


## Công nghệ sử dụng

- FastAPI - web framework
- SQLAlchemy 2.0 - ORM
- PyMySQL - MySQL driver
- Pydantic v2 - validate dữ liệu
- Passlib (bcrypt) - hash mật khẩu
- python-jose - xử lý JWT (Tiết 2)

## Ghi chú

- File `.env` không được commit lên git, chỉ commit `.env.example`.
- Chạy `pip freeze > requirements.txt` sau khi cài thêm package mới để chốt version.