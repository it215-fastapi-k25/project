from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field , field_validator
from app.models.research_project import MemberRole


class ResearchProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000) 
    
    @field_validator("name") 
    @classmethod 
    def name_must_not_be_blank(cls,v:str) -> str : 
        stripped = v.strip() 
        if not stripped : 
            raise ValueError("Project name cannot be blank")
        return stripped


class ResearchProjectCreate(ResearchProjectBase):
    pass


class ResearchProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)


class ResearchProjectResponse(ResearchProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime


class ResearchMemberCreate(BaseModel):
    user_id: int = Field(gt=0)


class ResearchMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    user_id: int
    role: MemberRole
    joined_at: datetime