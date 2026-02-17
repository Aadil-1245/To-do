from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID 

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    status_id: int
    project_id: int
    assigned_to: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None

class TaskMove(BaseModel):
    new_status_id: int

class TaskResponse(TaskBase):
    id: int
    status_id: int
    project_id: int
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
