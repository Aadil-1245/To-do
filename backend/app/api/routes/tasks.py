from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.base import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskMove
from app.schemas.task_comment import TaskCommentCreate, TaskCommentResponse
from app.services import task_service
from app.crud import task_comment as task_comment_crud
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await task_service.create_task(db, task, current_user)

@router.patch("/{task_id}/move", response_model=TaskResponse)
async def move_task(
    task_id: int,
    task_move: TaskMove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await task_service.move_task(db, task_id, task_move, current_user)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await task_service.delete_task(db, task_id, current_user)

@router.get("/project/{project_id}", response_model=List[TaskResponse])
async def get_project_tasks(
    project_id: int,
    status_id: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await task_service.get_project_tasks(
        db, project_id, current_user, status_id, priority, assigned_to, limit, offset
    )

@router.get("/board/{project_id}")
async def get_kanban_board(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await task_service.get_kanban_board(db, project_id, current_user)

@router.post("/{task_id}/comments", response_model=TaskCommentResponse)
async def add_task_comment(
    task_id: int,
    comment: TaskCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_comment = await task_comment_crud.create_comment(db, task_id, comment, current_user.id)
    await db.commit()
    await db.refresh(db_comment)
    
    # Get user name for response
    comment_response = TaskCommentResponse(
        id=db_comment.id,
        task_id=db_comment.task_id,
        user_id=db_comment.user_id,
        comment=db_comment.comment,
        created_at=db_comment.created_at,
        user_name=current_user.name
    )
    return comment_response

@router.get("/{task_id}/comments")
async def get_task_comments(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await task_comment_crud.get_task_comments(db, task_id)
