from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.research_project import ResearchProject, ResearchMember, MemberRole
from app.core.exceptions import NotFoundException, ForbiddenException


def get_project_or_404(db: Session, project_id: int) -> ResearchProject:
    project = db.query(ResearchProject).filter(
        ResearchProject.id == project_id,
        # update đk về phần soft delete -> taisetsu
        ResearchProject.is_deleted == False,
    ).first()
    if project is None:
        raise NotFoundException("Research project not found")
    return project


def get_membership_or_none(db: Session, project_id: int, user_id: int):
    return db.query(ResearchMember).filter(
        ResearchMember.project_id == project_id, ResearchMember.user_id == user_id
    ).first()


def require_project_member(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchProject:
    project = get_project_or_404(db, project_id)
    if get_membership_or_none(db, project_id, current_user.id) is None:
        raise ForbiddenException("You are not a member of this project")
    return project


def require_project_owner(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchProject:
    project = get_project_or_404(db, project_id)
    membership = get_membership_or_none(db, project_id, current_user.id)
    if membership is None or membership.role != MemberRole.OWNER:
        raise ForbiddenException("Only the project owner can perform this action")
    return project 