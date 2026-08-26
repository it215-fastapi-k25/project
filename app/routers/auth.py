from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, RefreshRequest, AccessTokenResponse
from app.services.auth_service import register_user, login_with_refresh, refresh_access_token
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user_in)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request ,form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    access_token, refresh_token = login_with_refresh(db, form_data.username, form_data.password)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    new_access_token = refresh_access_token(db, payload.refresh_token)
    return AccessTokenResponse(access_token=new_access_token)