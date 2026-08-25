from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.research_task import TaskStatus, TaskPriority


class ResearchTaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[int] = Field(default=None, gt=0)


class ResearchTaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = Field(default=None, gt=0)


class ResearchTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    title: str
    description: Optional[str]
    assignee_id: Optional[int]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime


class PaginatedTasks(BaseModel):
    items: list[ResearchTaskResponse]
    total: int
    page: int
    size: int