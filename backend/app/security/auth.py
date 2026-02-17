from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Prefer bcrypt_sha256 to avoid bcrypt's 72-byte password limit while
# keeping plain bcrypt in the schemes list for backward compatibility
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    print(f"[DEBUG] Creating token with data: {to_encode}")
    print(f"[DEBUG] Using SECRET_KEY: {settings.SECRET_KEY[:10]}...")
    print(f"[DEBUG] Algorithm: {settings.ALGORITHM}")
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    print(f"[DEBUG] Created token: {encoded_jwt[:50]}...")
    return encoded_jwt

def decode_access_token(token: str):
    try:
        print(f"[DEBUG] ===== TOKEN DECODE START =====")
        print(f"[DEBUG] Token (first 50 chars): {token[:50]}")
        print(f"[DEBUG] SECRET_KEY (first 10 chars): {settings.SECRET_KEY[:10]}")
        print(f"[DEBUG] Algorithm: {settings.ALGORITHM}")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        print(f"[DEBUG] ✅ Successfully decoded payload: {payload}")
        print(f"[DEBUG] ===== TOKEN DECODE SUCCESS =====")
        return payload
    except JWTError as e:
        print(f"[DEBUG] ❌ JWT ERROR: {str(e)}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        print(f"[DEBUG] ===== TOKEN DECODE FAILED =====")
        return None
    except Exception as e:
        print(f"[DEBUG] ❌ UNEXPECTED ERROR: {str(e)}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        return None
