from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.crud import task as task_crud, project as project_crud, status as status_crud, user as user_crud
from app.schemas.task import TaskCreate, TaskUpdate, TaskMove
from app.models.user import User
from app.models.project_member import ProjectMember
from typing import Optional

async def is_project_member(db: AsyncSession, user_id: int, project_id: int) -> tuple[bool, str]:
    """Check if user is project member and return role"""
    # Check if owner
    project = await project_crud.get_project_by_id(db, project_id)
    if project and project.owner_id == user_id:
        return True, "leader"
    
    # Check if team member
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.user_id == user_id,
            ProjectMember.project_id == project_id
        )
    )
    membership = result.scalar_one_or_none()
    if membership:
        return True, membership.role
    
    return False, None

async def create_task(db: AsyncSession, task: TaskCreate, current_user: User):
    try:
        project = await project_crud.get_project_by_id(db, task.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create tasks in this project"
            )
        
        task_status = await status_crud.get_status_by_id(db, task.status_id)
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Status not found"
            )
        
        if task.assigned_to:
            assigned_user = await user_crud.get_user_by_id(db, task.assigned_to)
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned user not found"
                )
        
        db_task = await task_crud.create_task(db, task)
        await db.commit()
        return db_task
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def move_task(db: AsyncSession, task_id: int, task_move: TaskMove, current_user: User):
    try:
        task = await task_crud.get_task_by_id(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check if user is project member or leader
        is_member, role = await is_project_member(db, current_user.id, task.project_id)
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to move this task"
            )
        
        # Only assigned user can move the task (or anyone if task is unassigned)
        if task.assigned_to is not None and task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned user can move this task"
            )
        
        new_status = await status_crud.get_status_by_id(db, task_move.new_status_id)
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New status not found"
            )
        
        updated_task = await task_crud.move_task(db, task, task_move.new_status_id)
        await db.commit()
        return updated_task
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def delete_task(db: AsyncSession, task_id: int, current_user: User):
    try:
        task = await task_crud.get_task_by_id(db, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        project = await project_crud.get_project_by_id(db, task.project_id)
        
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task"
            )
        
        await task_crud.soft_delete_task(db, task)
        await db.commit()
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def get_project_tasks(
    db: AsyncSession,
    project_id: int,
    current_user: User,
    status_id: Optional[int] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
):
    project = await project_crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view tasks in this project"
        )
    
    return await task_crud.get_project_tasks(
        db, project_id, status_id, priority, assigned_to, limit, offset
    )

async def get_kanban_board(db: AsyncSession, project_id: int, current_user: User):
    project = await project_crud.get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is project member or leader
    is_member, role = await is_project_member(db, current_user.id, project_id)
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    statuses = await status_crud.get_project_statuses(db, project_id)
    
    # Both leaders and members see all tasks
    tasks = await task_crud.get_tasks_by_status(db, project_id)
    
    # Get assigned user info for each task
    tasks_with_users = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status_id": task.status_id,
            "assigned_to": task.assigned_to,
            "assigned_user_name": None,
            "assigned_user_email": None
        }
        
        if task.assigned_to:
            assigned_user = await user_crud.get_user_by_id(db, task.assigned_to)
            if assigned_user:
                task_dict["assigned_user_name"] = assigned_user.name
                task_dict["assigned_user_email"] = assigned_user.email
        
        tasks_with_users.append(task_dict)
    
    board = []
    for status_obj in statuses:
        status_tasks = [task for task in tasks_with_users if task["status_id"] == status_obj.id]
        board.append({
            "status_id": status_obj.id,
            "status_name": status_obj.name,
            "tasks": status_tasks,
            "user_role": role,
            "current_user_id": current_user.id  # Send current user ID to frontend
        })
    
    return board
