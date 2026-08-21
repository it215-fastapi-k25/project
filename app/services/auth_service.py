from sqlalchemy.orm import Session 
from app.models.user import User 
from app.schemas.user import UserCreate 
from app.core.security import hash_password , verify_password , create_access_token , create_refresh_token
from app.core.exceptions import ConflictException , UnauthorizedException 
from app.core.config import settings
from jose import jwt, JWTError



def register_user(db: Session, user_in: UserCreate) -> User :  
    existing = db.query(User).filter(User.email == user_in.email).first() 
    if existing: 
        raise ConflictException("Email already registered") 
    user = User(
        email=user_in.email,
        full_name= user_in.full_name,
        password_hash = hash_password(user_in.password) 
    ) 
    db.add(user) 
    db.commit() 
    db.refresh(user) 
    return user 

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedException("Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedException("Account is inactive")
    return user 


def login_user(db: Session, email: str, password: str) -> str:
    user = authenticate_user(db, email, password)
    return create_access_token(user.id, user.role.value) 

def login_with_refresh(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id, user.role.value)
    return access_token, refresh_token


def refresh_access_token(db: Session, refresh_token: str) -> str:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise UnauthorizedException("Invalid refresh token")
    if payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid token type")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")
    return create_access_token(user.id, user.role.value)