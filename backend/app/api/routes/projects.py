from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, AddTeamMembersRequest
from app.services import project_service
from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.create_project(db, project, current_user)

@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.get_user_projects(db, current_user)

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.delete_project(db, project_id, current_user)

@router.post("/{project_id}/members")
async def add_team_members(
    project_id: int,
    request: AddTeamMembersRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.add_team_members(db, project_id, request.emails, current_user)

@router.get("/{project_id}/members")
async def get_project_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all members of a project including the owner"""
    return await project_service.get_project_members(db, project_id, current_user)


@router.get("/available")
async def get_available_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects that the user is NOT a member of"""
    return await project_service.get_available_projects(db, current_user)
