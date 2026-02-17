from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.project import Project
from app.schemas.project import ProjectCreate
from typing import Any


async def create_project(db: AsyncSession, project: ProjectCreate, owner_id: int):
    db_project = Project(
        title=project.title,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        technology_stack=project.technology_stack,
        team_size=project.team_size,
        owner_id=owner_id
    )
    db.add(db_project)
    await db.flush()
    await db.refresh(db_project)
    return db_project

async def get_project_by_id(db: AsyncSession, project_id: int):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()

async def get_user_projects(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Project).where(Project.owner_id == user_id, Project.deleted_at.is_(None))
    )
    return result.scalars().all()

async def soft_delete_project(db: AsyncSession, project: Project):
    from datetime import datetime
    project.deleted_at = datetime.utcnow()
    await db.flush()
    await db.refresh(project)
    return project
