from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 
MAX_PASSWORD_BYTES = 72 

# Hàm băm mật khẩu 
def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore") 
    return pwd_context.hash(truncated) 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore") 
    return pwd_context.verify(truncated, hashed_password) 

