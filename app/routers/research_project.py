from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_project_member, require_project_owner
from app.models.user import User
from app.models.research_project import ResearchProject
from app.schemas.research_project import (
    ResearchProjectCreate, ResearchProjectUpdate, ResearchProjectResponse,
    ResearchMemberCreate, ResearchMemberResponse,
)
from app.services import research_project_service as service

router = APIRouter(prefix="/research-projects", tags=["Research Projects"])


@router.post("", response_model=ResearchProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ResearchProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.create_project(db, current_user.id, data)


@router.get("", response_model=List[ResearchProjectResponse])
def list_projects(search: Optional[str] = Query(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_my_projects(db, current_user.id, search)


@router.get("/{project_id}", response_model=ResearchProjectResponse)
def get_project_detail(project: ResearchProject = Depends(require_project_member)):
    return project


@router.patch("/{project_id}", response_model=ResearchProjectResponse)
def update_project(data: ResearchProjectUpdate, project: ResearchProject = Depends(require_project_owner), db: Session = Depends(get_db)):
    return service.update_project(db, project, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project: ResearchProject = Depends(require_project_owner), db: Session = Depends(get_db)):
    service.delete_project(db, project)


@router.post("/{project_id}/members", response_model=ResearchMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(data: ResearchMemberCreate, project: ResearchProject = Depends(require_project_owner), db: Session = Depends(get_db)):
    return service.add_member(db, project.id, data.user_id)


@router.get("/{project_id}/members", response_model=List[ResearchMemberResponse])
def list_members(project: ResearchProject = Depends(require_project_member), db: Session = Depends(get_db)):
    return service.list_members(db, project.id)


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(user_id: int, project: ResearchProject = Depends(require_project_owner), db: Session = Depends(get_db)):
    service.remove_member(db, project.id, user_id)