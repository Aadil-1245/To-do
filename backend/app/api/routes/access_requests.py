from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas.access_request import AccessRequestCreate, AccessRequestResponse, AccessRequestApprove
from app.services import access_request_service
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/access-requests", tags=["Access Requests"])

@router.post("", response_model=AccessRequestResponse)
async def request_project_creation(
    request: AccessRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request permission to create projects"""
    return await access_request_service.request_project_creation(db, current_user, request)

@router.get("/pending", response_model=List[AccessRequestResponse])
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending access requests (for approvers only)"""
    return await access_request_service.get_all_pending_requests(db, current_user)

@router.post("/approve")
async def approve_request(
    approval: AccessRequestApprove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject an access request"""
    return await access_request_service.approve_or_reject_request(
        db, approval.request_id, approval.approved, current_user
    )
