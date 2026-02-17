from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

async def create_notification(db: AsyncSession, notification: NotificationCreate):
    db_notification = Notification(
        user_id=notification.user_id,
        message=notification.message,
        type=notification.type,
        related_id=notification.related_id
    )
    db.add(db_notification)
    await db.flush()
    await db.refresh(db_notification)
    return db_notification

async def get_user_notifications(db: AsyncSession, user_id: int, unread_only: bool = False):
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.order_by(Notification.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def mark_as_read(db: AsyncSession, notification_id: int):
    await db.execute(
        update(Notification)
        .where(Notification.id == notification_id)
        .values(is_read=True)
    )
    await db.flush()

async def mark_all_as_read(db: AsyncSession, user_id: int):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.flush()

async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    return result.scalar() or 0
