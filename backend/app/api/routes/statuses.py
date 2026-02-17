from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas.status import StatusCreate, StatusUpdate, StatusResponse
from app.services import status_service
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/statuses", tags=["Statuses"])

@router.post("", response_model=StatusResponse)
async def create_status(
    status: StatusCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await status_service.create_status(db, status, current_user)

@router.patch("/{status_id}", response_model=StatusResponse)
async def update_status(
    status_id: int,
    status_update: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await status_service.update_status(db, status_id, status_update, current_user)

@router.get("/project/{project_id}", response_model=List[StatusResponse])
async def get_project_statuses(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await status_service.get_project_statuses(db, project_id, current_user)
