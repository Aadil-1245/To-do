from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class StatusBase(BaseModel):
    name: str
    position: UUID

class StatusCreate(StatusBase):
    project_id: int 

class StatusUpdate(BaseModel):
    name: str

class StatusResponse(StatusBase):
    id: int 
    project_id: int 
    created_at: datetime
    
    model_config = {"from_attributes": True}
