from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_project_member, require_task_member, require_task_update_permission
from app.models.user import User
from app.models.research_project import ResearchProject
from app.models.research_task import ResearchTask, TaskStatus, TaskPriority
from app.schemas.research_task import ResearchTaskCreate, ResearchTaskUpdate, ResearchTaskResponse, PaginatedTasks
from app.services import research_task_service as service

router = APIRouter(tags=["Research Tasks"])


@router.post("/research-projects/{project_id}/research-tasks", response_model=ResearchTaskResponse,
             status_code=status.HTTP_201_CREATED, summary="Tạo nhiệm vụ nghiên cứu mới trong đề tài")
def create_task(data: ResearchTaskCreate, project: ResearchProject = Depends(require_project_member),
                 current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.create_task(db, project, data, current_user.id)


@router.get("/research-projects/{project_id}/research-tasks", response_model=PaginatedTasks,
            summary="Danh sách nhiệm vụ, hỗ trợ filter/search/pagination/sort")
def list_tasks(
    project: ResearchProject = Depends(require_project_member),
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    priority: Optional[TaskPriority] = Query(default=None),
    assignee_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at", pattern="^(created_at|due_date)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = service.list_tasks(db, project.id, status_filter, priority, assignee_id, search, sort_by, sort_order, page, size)
    return PaginatedTasks(items=items, total=total, page=page, size=size)


@router.get("/research-tasks/{task_id}", response_model=ResearchTaskResponse, summary="Chi tiết nhiệm vụ")
def get_task_detail(task: ResearchTask = Depends(require_task_member)):
    return task


@router.patch("/research-tasks/{task_id}", response_model=ResearchTaskResponse,
              summary="Cập nhật nhiệm vụ, chi Owner hoac Assignee")
def update_task(data: ResearchTaskUpdate, task: ResearchTask = Depends(require_task_update_permission),
                 current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.update_task(db, task, data, current_user.id)


@router.delete("/research-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Xóa nhiệm vụ, chi Owner hoac Assignee")
def delete_task(task: ResearchTask = Depends(require_task_update_permission),
                 current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service.delete_task(db, task, current_user.id)