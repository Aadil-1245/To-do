from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.security.auth import decode_access_token
from app.crud import user as user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    print(f"[DEBUG] ===== GET_CURRENT_USER START =====")
    print(f"[DEBUG] Raw token received from OAuth2PasswordBearer:")
    print(f"[DEBUG] Token length: {len(token)}")
    print(f"[DEBUG] Token (first 100 chars): {token[:100]}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    
    if payload is None:
        print("[DEBUG] ❌ Payload is None - token decode failed")
        print("[DEBUG] ===== GET_CURRENT_USER FAILED =====")
        raise credentials_exception
    
    # Get user_id as string from JWT (industry standard)
    user_id_str: str = payload.get("sub")
    print(f"[DEBUG] User ID from token (string): {user_id_str}")
    
    if user_id_str is None:
        print("[DEBUG] ❌ No 'sub' in payload")
        raise credentials_exception
    
    # Convert to int for database query
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        print(f"[DEBUG] ❌ Invalid user_id format: {user_id_str}")
        raise credentials_exception
    
    user = await user_crud.get_user_by_id(db, user_id=user_id)
    print(f"[DEBUG] User found: {user.email if user else 'None'}")
    
    if user is None or user.deleted_at is not None:
        print("[DEBUG] ❌ User not found or deleted")
        raise credentials_exception
    
    print(f"[DEBUG] ✅ Authentication successful for user: {user.email}")
    print("[DEBUG] ===== GET_CURRENT_USER SUCCESS =====")
    return user
