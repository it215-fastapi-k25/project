from app.db.database import SessionLocal
from app.db.init_db import init_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.research_project import ResearchProject, ResearchMember, MemberRole
from app.models.research_task import ResearchTask, TaskStatus, TaskPriority


def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("Database already seeded, skipping.")
            return

        admin = User(
            email="admin@researchresearch-demo.com",
            password_hash=hash_password("Admin@12345"),
            full_name="System Admin",
            role=UserRole.ADMIN,
        )
        owner = User(
            email="owner@research-demo.com",
            password_hash=hash_password("Owner@12345"),
            full_name="Nguyen Van Owner",
            role=UserRole.USER,
        )
        member = User(
            email="member@researchresearch-demo.com",
            password_hash=hash_password("Member@12345"),
            full_name="Tran Thi Member",
            role=UserRole.USER,
        )
        db.add_all([admin, owner, member])
        db.flush()

        project = ResearchProject(
            name="Nguyên cứu ứng dụng AI trong y tế",
            description="Đề tài nghiên cứu ứng dụng mô hình học máy trong chẩn đoán hình ảnh y khoa.",
            owner_id=owner.id,
        )
        db.add(project)
        db.flush()

        db.add_all([
            ResearchMember(project_id=project.id, user_id=owner.id, role=MemberRole.OWNER),
            ResearchMember(project_id=project.id, user_id=member.id, role=MemberRole.MEMBER),
        ])

        db.add_all([
            ResearchTask(
                project_id=project.id,
                title="Thu thập và tiền xử lý dữ liệu",
                description="Thu thập tập dữ liệu ảnh X-quang và tiền xử lý.",
                assignee_id=member.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
            ),
            ResearchTask(
                project_id=project.id,
                title="Viết báo cáo tổng quan tài liệu",
                description="Tổng hợp các nghiên cứu liên quan đã công bố.",
                assignee_id=owner.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
            ),
        ])

        db.commit()
        print("Seed data inserted successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()