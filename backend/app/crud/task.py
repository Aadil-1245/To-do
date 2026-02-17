from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from typing import Optional

async def create_task(db: AsyncSession, task: TaskCreate):
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        status_id=task.status_id,
        project_id=task.project_id,
        assigned_to=task.assigned_to
    )
    db.add(db_task)
    await db.flush()
    await db.refresh(db_task)
    return db_task

async def get_task_by_id(db: AsyncSession, task_id: int):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()

async def get_project_tasks(
    db: AsyncSession,
    project_id: int,
    status_id: Optional[int] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
):
    query = select(Task).where(Task.project_id == project_id, Task.deleted_at.is_(None))
    
    if status_id:
        query = query.where(Task.status_id == status_id)
    if priority:
        query = query.where(Task.priority == priority)
    if assigned_to:
        query = query.where(Task.assigned_to == assigned_to)
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()

async def update_task(db: AsyncSession, task: Task, task_update: TaskUpdate):
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.assigned_to is not None:
        task.assigned_to = task_update.assigned_to
    
    await db.flush()
    await db.refresh(task)
    return task

async def move_task(db: AsyncSession, task: Task, new_status_id: int):
    task.status_id = new_status_id
    await db.flush()
    await db.refresh(task)
    return task

async def soft_delete_task(db: AsyncSession, task: Task):
    from datetime import datetime
    task.deleted_at = datetime.utcnow()
    await db.flush()
    await db.refresh(task)
    return task

async def get_tasks_by_status(db: AsyncSession, project_id: int):
    result = await db.execute(
        select(Task).where(Task.project_id == project_id, Task.deleted_at.is_(None))
    )
    return result.scalars().all()

async def get_tasks_by_assignee(db: AsyncSession, project_id: int, user_id: int):
    """Get all tasks assigned to a specific user in a project"""
    result = await db.execute(
        select(Task).where(
            Task.project_id == project_id,
            Task.assigned_to == user_id,
            Task.deleted_at.is_(None)
        )
    )
    return result.scalars().all()
