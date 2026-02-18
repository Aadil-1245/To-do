from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.crud import status as status_crud, project as project_crud
from app.schemas.status import StatusCreate, StatusUpdate
from app.models.user import User

async def create_status(db: AsyncSession, status: StatusCreate, current_user: User):
    try:
        project = await project_crud.get_project_by_id(db, status.project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this project"
            )
        
        db_status = await status_crud.create_status(db, status)
        await db.commit()
        return db_status
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def update_status(db: AsyncSession, status_id: int, status_update: StatusUpdate, current_user: User):
    try:
        db_status = await status_crud.get_status_by_id(db, status_id)
        
        if not db_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Status not found"
            )
        
        project = await project_crud.get_project_by_id(db, db_status.project_id)
        
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this status"
            )
        
        updated_status = await status_crud.update_status_name(db, db_status, status_update.name)
        await db.commit()
        return updated_status
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def get_project_statuses(db: AsyncSession, project_id: int, current_user: User):
    from sqlalchemy import select
    from app.models.project_member import ProjectMember
    
    project = await project_crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is project owner or team member
    is_member = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        )
    )
    
    if project.owner_id != current_user.id and not is_member.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    return await status_crud.get_project_statuses(db, project_id)
