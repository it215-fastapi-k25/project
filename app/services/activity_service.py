from typing import Optional
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog


def log_activity(db: Session, project_id: Optional[int], actor_id: int, action: str, detail: Optional[str] = None) -> None:
    db.add(ActivityLog(project_id=project_id, actor_id=actor_id, action=action, detail=detail))