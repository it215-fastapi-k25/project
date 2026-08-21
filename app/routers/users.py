from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db.database import get_db
from app.dependencies.auth import get_admin_user, get_current_user
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=List[UserResponse])
def list_users(
    search: Optional[str] = Query(default=None, description="Tìm theo tên hoặc email"),
    is_active: Optional[bool] = Query(default=None, description="Lọc theo trạng thái tài khoản"),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(User.full_name.ilike(pattern), User.email.ilike(pattern)))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.all()