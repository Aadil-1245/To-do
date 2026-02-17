from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas.notification import NotificationResponse
from app.crud import notification as notification_crud
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's notifications"""
    return await notification_crud.get_user_notifications(db, current_user.id, unread_only)

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread notifications"""
    count = await notification_crud.get_unread_count(db, current_user.id)
    return {"count": count}

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    await notification_crud.mark_as_read(db, notification_id)
    await db.commit()
    return {"message": "Notification marked as read"}

@router.post("/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    await notification_crud.mark_all_as_read(db, current_user.id)
    await db.commit()
    return {"message": "All notifications marked as read"}
