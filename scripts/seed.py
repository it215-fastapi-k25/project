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
            name="Nghien cuu ung dung AI trong Y te",
            description="De tai nghien cuu ung dung mo hinh hoc may trong chan doan hinh anh y khoa.",
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
                title="Thu thap va tien xu ly du lieu",
                description="Thu thap tap du lieu anh X-quang va tien xu ly.",
                assignee_id=member.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
            ),
            ResearchTask(
                project_id=project.id,
                title="Viet bao cao tong quan tai lieu",
                description="Tong hop cac nghien cuu lien quan da cong bo.",
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