from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.crud import user as user_crud
from app.schemas.user import UserCreate
from app.security.auth import verify_password, create_access_token

async def register_user(db: AsyncSession, user: UserCreate):
    try:
        existing_user = await user_crud.get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        db_user = await user_crud.create_user(db, user)
        await db.commit()
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def login_user(db: AsyncSession, email: str, password: str):
    user = await user_crud.get_user_by_email(db, email=email)
    
    if not user or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    try:
        password_ok = verify_password(password, user.hashed_password)
    except ValueError as e:
        # bcrypt raises ValueError for passwords longer than 72 bytes.
        # Log length for debugging (do NOT log the actual password in production).
        try:
            pw_len = len(password.encode('utf-8'))
        except Exception:
            pw_len = None
        print(f"[DEBUG] Password verification error: {e}; password_len={pw_len}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Convert user.id to string for JWT (industry standard)
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
