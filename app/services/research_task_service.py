from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.research_task import ResearchTask, TaskStatus, TaskPriority
from app.models.research_project import ResearchProject
from app.schemas.research_task import ResearchTaskCreate, ResearchTaskUpdate
from app.core.exceptions import BadRequestException
from app.dependencies.permissions import get_membership_or_none
from app.services.research_project_service import escape_like, log_activity


def validate_assignee(db: Session, project_id: int, assignee_id: Optional[int]) -> None:
    if assignee_id is None:
        return
    if get_membership_or_none(db, project_id, assignee_id) is None:
        raise BadRequestException("Assignee must be a member of this project")


def create_task(db: Session, project: ResearchProject, data: ResearchTaskCreate, actor_id: int) -> ResearchTask:
    validate_assignee(db, project.id, data.assignee_id)
    task = ResearchTask(
        project_id=project.id, title=data.title, description=data.description,
        due_date=data.due_date, priority=data.priority, assignee_id=data.assignee_id,
    )
    db.add(task)
    log_activity(db, project.id, actor_id, "CREATE_TASK", f"Created task '{data.title}'")
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session, project_id: int,
    status_filter: Optional[TaskStatus] = None, priority_filter: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None, search: Optional[str] = None,
    sort_by: str = "created_at", sort_order: str = "desc", page: int = 1, size: int = 20,
) -> tuple[list[ResearchTask], int]:
    query = db.query(ResearchTask).filter(ResearchTask.project_id == project_id)
    conditions = []
    if status_filter is not None:
        conditions.append(ResearchTask.status == status_filter)
    if priority_filter is not None:
        conditions.append(ResearchTask.priority == priority_filter)
    if assignee_id is not None:
        conditions.append(ResearchTask.assignee_id == assignee_id)
    if search:
        conditions.append(ResearchTask.title.ilike(f"%{escape_like(search)}%", escape="\\"))
    if conditions:
        query = query.filter(and_(*conditions))
    sort_column = ResearchTask.created_at if sort_by == "created_at" else ResearchTask.due_date
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return items, total


def update_task(db: Session, task: ResearchTask, data: ResearchTaskUpdate, actor_id: int) -> ResearchTask:
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise BadRequestException("No fields provided to update")
    if "assignee_id" in changes:
        validate_assignee(db, task.project_id, changes["assignee_id"])
    for field, value in changes.items():
        setattr(task, field, value)
    log_activity(db, task.project_id, actor_id, "UPDATE_TASK", f"Updated task_id={task.id} fields: {list(changes.keys())}")
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: ResearchTask, actor_id: int) -> None:
    project_id, task_id = task.project_id, task.id
    db.delete(task)
    log_activity(db, project_id, actor_id, "DELETE_TASK", f"Deleted task_id={task_id}")
    db.commit()