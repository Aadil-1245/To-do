from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.access_request import AccessRequest
from app.models.user import User
from app.schemas.access_request import AccessRequestCreate

async def create_access_request(db: AsyncSession, requester_id: int, request: AccessRequestCreate):
    db_request = AccessRequest(
        requester_id=requester_id,
        request_type="create_project",
        reason=request.reason,
        status="pending"
    )
    db.add(db_request)
    await db.flush()
    await db.refresh(db_request)
    return db_request

async def get_pending_requests(db: AsyncSession):
    """Get all pending access requests with user and project info"""
    from app.models.project import Project
    
    result = await db.execute(
        select(AccessRequest, User.name, User.email, Project.title)
        .join(User, AccessRequest.requester_id == User.id)
        .outerjoin(Project, AccessRequest.project_id == Project.id)
        .where(AccessRequest.status == "pending")
        .order_by(AccessRequest.created_at.desc())
    )
    
    requests = []
    for request, user_name, user_email, project_title in result.all():
        request_dict = {
            "id": request.id,
            "requester_id": request.requester_id,
            "requester_name": user_name,
            "requester_email": user_email,
            "approver_id": request.approver_id,
            "project_id": request.project_id,
            "project_title": project_title,
            "request_type": request.request_type,
            "reason": request.reason,
            "status": request.status,
            "created_at": request.created_at
        }
        requests.append(request_dict)
    return requests

async def get_user_requests(db: AsyncSession, user_id: int):
    """Get all requests made by a specific user"""
    result = await db.execute(
        select(AccessRequest)
        .where(AccessRequest.requester_id == user_id)
        .order_by(AccessRequest.created_at.desc())
    )
    return result.scalars().all()

async def approve_request(db: AsyncSession, request_id: int, approver_id: int):
    result = await db.execute(
        select(AccessRequest).where(AccessRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    
    if request:
        request.status = "approved"
        request.approver_id = approver_id
        
        # Grant permission to user
        user_result = await db.execute(
            select(User).where(User.id == request.requester_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.can_create_projects = True
        
        await db.flush()
    return request

async def reject_request(db: AsyncSession, request_id: int, approver_id: int):
    result = await db.execute(
        select(AccessRequest).where(AccessRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    
    if request:
        request.status = "rejected"
        request.approver_id = approver_id
        await db.flush()
    return request


async def create_project_join_request(db: AsyncSession, requester_id: int, project_id: int, reason: str = None):
    """Create a request to join a specific project"""
    db_request = AccessRequest(
        requester_id=requester_id,
        project_id=project_id,
        request_type="join_project",
        reason=reason,
        status="pending"
    )
    db.add(db_request)
    await db.flush()
    await db.refresh(db_request)
    return db_request

async def get_user_project_requests(db: AsyncSession, user_id: int, project_id: int):
    """Get all requests made by a user for a specific project"""
    result = await db.execute(
        select(AccessRequest)
        .where(
            AccessRequest.requester_id == user_id,
            AccessRequest.project_id == project_id
        )
        .order_by(AccessRequest.created_at.desc())
    )
    return result.scalars().all()

async def get_request_by_id(db: AsyncSession, request_id: int):
    """Get a specific request by ID"""
    result = await db.execute(
        select(AccessRequest).where(AccessRequest.id == request_id)
    )
    return result.scalar_one_or_none()
