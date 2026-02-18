from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from typing import List
from uuid import uuid4
from app.crud import project as project_crud, status as status_crud, notification as notification_crud
import logging

logger = logging.getLogger(__name__)
from app.schemas.project import ProjectCreate
from app.schemas.status import StatusCreate
from app.schemas.notification import NotificationCreate
from app.models.user import User
from app.models.task import Task
from app.models.project_member import ProjectMember

async def create_project(db: AsyncSession, project: ProjectCreate, current_user: User):
    try:
        # Allow all users to create projects (previously required can_create_projects)
        db_project = await project_crud.create_project(db, project, current_user.id)
        
        # Add project creator as team leader
        team_leader = ProjectMember(
            project_id=db_project.id,
            user_id=current_user.id,
            role="leader"
        )
        db.add(team_leader)
        
        # Create default statuses for the project
        default_statuses = [
            StatusCreate(name="Todo", position=uuid4(), project_id=db_project.id),
            StatusCreate(name="In Progress", position=uuid4(), project_id=db_project.id),
            StatusCreate(name="Done", position=uuid4(), project_id=db_project.id)
        ]
        
        for st in default_statuses:
            await status_crud.create_status(db, st)
        
        await db.commit()
        return db_project
    except Exception as e:
        await db.rollback()
        logger.exception("Project creation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def get_user_projects(db: AsyncSession, current_user: User):
    # Get projects where user is owner OR team member
    result = await db.execute(
        select(project_crud.Project).join(
            ProjectMember,
            ProjectMember.project_id == project_crud.Project.id
        ).where(
            ProjectMember.user_id == current_user.id,
            project_crud.Project.deleted_at.is_(None)
        )
    )
    projects = result.scalars().all()
    
    # Calculate progress and add role for each project
    projects_with_progress = []
    for project in projects:
        progress = await calculate_project_progress(db, project.id)
        
        # Get user's role in this project
        role_result = await db.execute(
            select(ProjectMember.role).where(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == current_user.id
            )
        )
        user_role = role_result.scalar()
        
        project_dict = {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "technology_stack": project.technology_stack,
            "team_size": project.team_size,
            "owner_id": project.owner_id,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "progress": progress,
            "user_role": user_role  # leader or member
        }
        projects_with_progress.append(project_dict)
    
    return projects_with_progress

async def calculate_project_progress(db: AsyncSession, project_id: int) -> float:
    """Calculate project completion percentage based on tasks"""
    # Get total tasks
    total_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.deleted_at.is_(None)
        )
    )
    total_tasks = total_result.scalar() or 0
    
    if total_tasks == 0:
        return 0.0
    
    # Get completed tasks (tasks in "Done" status)
    completed_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.project_id == project_id,
            Task.deleted_at.is_(None),
            Task.status_id.in_(
                select(status_crud.Status.id).where(
                    status_crud.Status.project_id == project_id,
                    status_crud.Status.name == "Done"
                )
            )
        )
    )
    completed_tasks = completed_result.scalar() or 0
    
    return round((completed_tasks / total_tasks) * 100, 1)

async def delete_project(db: AsyncSession, project_id: int, current_user: User):
    try:
        project = await project_crud.get_project_by_id(db, project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this project"
            )
        
        await project_crud.soft_delete_project(db, project)
        await db.commit()
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def add_team_members(db: AsyncSession, project_id: int, emails: List[str], current_user: User):
    """Add team members to a project by their email addresses"""
    try:
        # Check if project exists and user is the leader
        project = await project_crud.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project leader can add team members"
            )
        
        added_members = []
        not_found_emails = []
        
        for email in emails:
            # Find user by email
            result = await db.execute(
                select(User).where(User.email == email.strip())
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Check if already a member
                existing = await db.execute(
                    select(ProjectMember).where(
                        ProjectMember.project_id == project_id,
                        ProjectMember.user_id == user.id
                    )
                )
                if not existing.scalar_one_or_none():
                    # Add as team member
                    member = ProjectMember(
                        project_id=project_id,
                        user_id=user.id,
                        role="member"
                    )
                    db.add(member)
                    added_members.append(email)
                    
                    # Create notification for the added member
                    notification = NotificationCreate(
                        user_id=user.id,
                        message=f"You have been added to project '{project.title}'",
                        type="project_assigned",
                        related_id=project_id
                    )
                    created_notif = await notification_crud.create_notification(db, notification)
                    print(f"✅ Created notification ID {created_notif.id} for user {user.email}")
            else:
                not_found_emails.append(email)
        
        await db.commit()
        
        return {
            "message": f"Added {len(added_members)} team members",
            "added": added_members,
            "not_found": not_found_emails
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def get_project_members(db: AsyncSession, project_id: int, current_user: User):
    """Get all members of a project including the owner"""
    try:
        # Check if project exists
        project = await project_crud.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if user is a member or owner
        is_owner = project.owner_id == current_user.id
        result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id
            )
        )
        is_member = result.scalar_one_or_none() is not None
        
        if not is_owner and not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view project members"
            )
        
        # Get all project members with user info
        members_result = await db.execute(
            select(ProjectMember, User).join(
                User, ProjectMember.user_id == User.id
            ).where(
                ProjectMember.project_id == project_id
            )
        )
        
        members = []
        for member, user in members_result.all():
            members.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": member.role
            })
        
        return members
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def get_available_projects(db: AsyncSession, current_user: User):
    """Get all projects that the user is NOT a member of"""
    try:
        # Get all projects
        all_projects_result = await db.execute(
            select(project_crud.Project).where(
                project_crud.Project.deleted_at.is_(None)
            )
        )
        all_projects = all_projects_result.scalars().all()
        
        # Get projects where user is a member
        user_projects_result = await db.execute(
            select(ProjectMember.project_id).where(
                ProjectMember.user_id == current_user.id
            )
        )
        user_project_ids = [row[0] for row in user_projects_result.all()]
        
        # Filter out projects where user is already a member
        available_projects = []
        for project in all_projects:
            if project.id not in user_project_ids:
                # Get owner info
                owner_result = await db.execute(
                    select(User).where(User.id == project.owner_id)
                )
                owner = owner_result.scalar_one_or_none()
                
                available_projects.append({
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "technology_stack": project.technology_stack,
                    "team_size": project.team_size,
                    "owner_name": owner.name if owner else "Unknown",
                    "created_at": project.created_at
                })
        
        return available_projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
