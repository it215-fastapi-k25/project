import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, UniqueConstraint , Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.database import Base


class MemberRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    # Thêm 2 cột soft-delete 
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="owned_projects")
    members: Mapped[list["ResearchMember"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    tasks: Mapped[list["ResearchTask"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"ResearchProject(id={self.id!r}, name={self.name!r})"


class ResearchMember(Base):
    __tablename__ = "research_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_user"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("research_projects.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["ResearchProject"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")

    def __repr__(self) -> str:
        return f"ResearchMember(project_id={self.project_id!r}, user_id={self.user_id!r}, role={self.role!r})"