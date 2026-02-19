from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.status import Status
from app.schemas.status import StatusCreate
from typing import Any


async def create_status(db: AsyncSession, status: StatusCreate):
    db_status = Status(
        name=status.name,
        position=status.position,
        project_id=status.project_id
    )
    db.add(db_status)
    await db.flush()
    await db.refresh(db_status)
    return db_status

async def get_status_by_id(db: AsyncSession, status_id: int):
    result = await db.execute(select(Status).where(Status.id == status_id))
    return result.scalar_one_or_none()

async def get_project_statuses(db: AsyncSession, project_id: int):
    result = await db.execute(
        select(Status).where(Status.project_id == project_id).order_by(Status.position)
    )
    return result.scalars().all()

async def update_status_name(db: AsyncSession, status: Status, name: str):
    status.name = name
    await db.flush()
    await db.refresh(status)
    return status
async def delete_status(db: AsyncSession, status_id: int):
    result = await db.execute(select(Status).where(Status.id == status_id))
    status = result.scalar_one_or_none()
    if status:
        await db.delete(status)
        await db.flush()
    return status