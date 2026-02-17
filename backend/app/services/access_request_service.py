from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.crud import access_request as access_request_crud, notification as notification_crud
from app.schemas.access_request import AccessRequestCreate
from app.schemas.notification import NotificationCreate
from app.models.user import User

async def request_project_creation(db: AsyncSession, current_user: User, request: AccessRequestCreate):
    """User requests permission to create projects OR join a specific project"""
    
    # If project_id is provided, it's a join request
    if request.project_id:
        # Check if project exists
        from app.crud import project as project_crud
        project = await project_crud.get_project_by_id(db, request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if already a member
        from app.models.project_member import ProjectMember
        from sqlalchemy import select
        result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == request.project_id,
                ProjectMember.user_id == current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this project"
            )
        
        # Check for pending request
        existing_requests = await access_request_crud.get_user_project_requests(
            db, current_user.id, request.project_id
        )
        pending = [r for r in existing_requests if r.status == "pending"]
        if pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending request for this project"
            )
        
        db_request = await access_request_crud.create_project_join_request(
            db, current_user.id, request.project_id, request.reason
        )
        await db.commit()
        
        return {
            "id": db_request.id,
            "requester_id": db_request.requester_id,
            "requester_name": current_user.name,
            "requester_email": current_user.email,
            "approver_id": db_request.approver_id,
            "project_id": db_request.project_id,
            "project_title": project.title,
            "request_type": db_request.request_type,
            "reason": db_request.reason,
            "status": db_request.status,
            "created_at": db_request.created_at
        }
    else:
        # Original: Request permission to create projects
        if current_user.can_create_projects:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have permission to create projects"
            )
        
        # Check if there's already a pending request
        existing_requests = await access_request_crud.get_user_requests(db, current_user.id)
        pending = [r for r in existing_requests if r.status == "pending" and r.request_type == "create_project"]
        
        if pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending request"
            )
        
        db_request = await access_request_crud.create_access_request(db, current_user.id, request)
        await db.commit()
        
        return {
            "id": db_request.id,
            "requester_id": db_request.requester_id,
            "requester_name": current_user.name,
            "requester_email": current_user.email,
            "approver_id": db_request.approver_id,
            "project_id": None,
            "project_title": None,
            "request_type": db_request.request_type,
            "reason": db_request.reason,
            "status": db_request.status,
            "created_at": db_request.created_at
        }

async def get_all_pending_requests(db: AsyncSession, current_user: User):
    """Get pending requests that the current user can approve"""
    if not current_user.can_create_projects:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view access requests"
        )
    
    # Get all pending requests
    all_requests = await access_request_crud.get_pending_requests(db)
    
    # Filter requests based on what user can approve
    filtered_requests = []
    for request in all_requests:
        # User can approve create_project requests (any leader)
        if request["request_type"] == "create_project":
            filtered_requests.append(request)
        # User can only approve join_project requests for their own projects
        elif request["request_type"] == "join_project" and request["project_id"]:
            from app.crud import project as project_crud
            project = await project_crud.get_project_by_id(db, request["project_id"])
            if project and project.owner_id == current_user.id:
                filtered_requests.append(request)
    
    return filtered_requests

async def approve_or_reject_request(db: AsyncSession, request_id: int, approved: bool, current_user: User):
    """Approve or reject an access request"""
    request = await access_request_crud.get_request_by_id(db, request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check permissions based on request type
    if request.request_type == "join_project":
        # For project join requests, only the project owner can approve
        from app.crud import project as project_crud
        project = await project_crud.get_project_by_id(db, request.project_id)
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can approve this request"
            )
    else:
        # For create_project requests, any user with can_create_projects can approve
        if not current_user.can_create_projects:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to approve requests"
            )
    
    if approved:
        if request.request_type == "join_project":
            # Add user to project as member
            from app.models.project_member import ProjectMember
            member = ProjectMember(
                project_id=request.project_id,
                user_id=request.requester_id,
                role="member"
            )
            db.add(member)
            
            request_obj = await access_request_crud.approve_request(db, request_id, current_user.id)
            message_text = "approved"
            
            # Get project info for notification
            from app.crud import project as project_crud
            project = await project_crud.get_project_by_id(db, request.project_id)
            
            # Create notification for requester
            if request_obj:
                notification = NotificationCreate(
                    user_id=request_obj.requester_id,
                    message=f"Your request to join project '{project.title}' has been approved!",
                    type="project_assigned",
                    related_id=request.project_id
                )
                await notification_crud.create_notification(db, notification)
        else:
            # Grant create_project permission
            request_obj = await access_request_crud.approve_request(db, request_id, current_user.id)
            message_text = "approved"
            
            if request_obj:
                notification = NotificationCreate(
                    user_id=request_obj.requester_id,
                    message=f"Your request to create projects has been approved!",
                    type="access_approved",
                    related_id=request_id
                )
                await notification_crud.create_notification(db, notification)
    else:
        request_obj = await access_request_crud.reject_request(db, request_id, current_user.id)
        message_text = "rejected"
        
        # Create notification for requester
        if request_obj:
            if request_obj.request_type == "join_project":
                from app.crud import project as project_crud
                project = await project_crud.get_project_by_id(db, request_obj.project_id)
                message = f"Your request to join project '{project.title}' has been rejected."
            else:
                message = f"Your request to create projects has been rejected."
            
            notification = NotificationCreate(
                user_id=request_obj.requester_id,
                message=message,
                type="access_rejected",
                related_id=request_id
            )
            await notification_crud.create_notification(db, notification)
    
    await db.commit()
    return {"message": f"Request {message_text}"}
