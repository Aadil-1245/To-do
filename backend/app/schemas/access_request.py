from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AccessRequestCreate(BaseModel):
    project_id: Optional[int] = None  # For join_project requests
    reason: Optional[str] = None

class AccessRequestResponse(BaseModel):
    id: int
    requester_id: int
    requester_name: str
    requester_email: str
    approver_id: Optional[int] = None
    project_id: Optional[int] = None
    project_title: Optional[str] = None
    request_type: str
    reason: Optional[str] = None
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

class AccessRequestApprove(BaseModel):
    request_id: int
    approved: bool  # True = approve, False = reject
