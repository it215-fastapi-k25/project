from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.research_task import TaskStatus, TaskPriority


class ResearchTaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM


class ResearchTaskCreate(ResearchTaskBase):
    assignee_id: Optional[int] = Field(default=None, gt=0)


class ResearchTaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")
        return self


class ResearchTaskResponse(ResearchTaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    assignee_id: Optional[int]
    status: TaskStatus
    created_at: datetime 
    
    