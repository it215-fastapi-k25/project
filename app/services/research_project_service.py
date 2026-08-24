from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.research_project import ResearchProject, ResearchMember, MemberRole
from app.models.user import User
from app.schemas.research_project import ResearchProjectCreate, ResearchProjectUpdate
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.dependencies.permissions import get_membership_or_none


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def create_project(db: Session, owner_id: int, data: ResearchProjectCreate) -> ResearchProject:
    project = ResearchProject(name=data.name, description=data.description, owner_id=owner_id)
    db.add(project)
    db.flush()
    membership = ResearchMember(project_id=project.id, user_id=owner_id, role=MemberRole.OWNER)
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project


def list_my_projects(db: Session, user_id: int, search: Optional[str] = None) -> list[ResearchProject]:
    query = (
        db.query(ResearchProject)
        .join(ResearchMember, ResearchMember.project_id == ResearchProject.id)
        .filter(ResearchMember.user_id == user_id)
    )
    if search:
        pattern = f"%{escape_like(search)}%"
        query = query.filter(ResearchProject.name.ilike(pattern, escape="\\"))
    return query.all()


def update_project(db: Session, project: ResearchProject, data: ResearchProjectUpdate) -> ResearchProject:
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise BadRequestException("No fields provided to update")
    for field, value in changes.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: ResearchProject) -> None:
    db.delete(project)
    db.commit()


def add_member(db: Session, project_id: int, target_user_id: int) -> ResearchMember:
    user = db.query(User).filter(User.id == target_user_id).first()
    if user is None:
        raise NotFoundException("User not found")
    if get_membership_or_none(db, project_id, target_user_id) is not None:
        raise ConflictException("User is already a member of this project")
    membership = ResearchMember(project_id=project_id, user_id=target_user_id, role=MemberRole.MEMBER)
    db.add(membership)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictException("User is already a member of this project")
    db.refresh(membership)
    return membership


def remove_member(db: Session, project_id: int, target_user_id: int) -> None:
    membership = get_membership_or_none(db, project_id, target_user_id)
    if membership is None:
        raise NotFoundException("Membership not found")
    if membership.role == MemberRole.OWNER:
        owner_count = db.query(ResearchMember).filter(
            ResearchMember.project_id == project_id, ResearchMember.role == MemberRole.OWNER
        ).count()
        if owner_count <= 1:
            raise BadRequestException("Cannot remove the last owner of the project")
    db.delete(membership)
    db.commit()


def list_members(db: Session, project_id: int) -> list[ResearchMember]:
    return db.query(ResearchMember).filter(ResearchMember.project_id == project_id).all()