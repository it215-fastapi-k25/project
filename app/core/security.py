from passlib.context import CryptContext

from datetime import datetime , timedelta , timezone 
from jose import jwt 
from app.core.config import settings  


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
MAX_PASSWORD_BYTES = 72 

# Hàm băm mật khẩu 
def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore") 
    return pwd_context.hash(truncated) 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore") 
    return pwd_context.verify(truncated, hashed_password) 

# Create access token 
def create_token(user_id: int, role: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(user_id), "role": role, "type": token_type, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: int, role: str) -> str:
    return create_token(user_id, role, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access")


def create_refresh_token(user_id: int, role: str) -> str:
    return create_token(user_id, role, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")