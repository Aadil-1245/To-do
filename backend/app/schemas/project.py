from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    technology_stack: Optional[str] = None
    team_size: Optional[UUID] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int

    owner_id: int
    created_at: datetime
    updated_at: datetime
    progress: Optional[float] = 0.0

    model_config = {"from_attributes": True}

class ProjectMemberAdd(BaseModel):
    email: str
    role: str = "member"

class AddTeamMembersRequest(BaseModel):
    emails: List[str]
