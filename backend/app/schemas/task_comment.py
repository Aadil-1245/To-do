from pydantic import BaseModel
from datetime import datetime
from uuid import UUID 

class TaskCommentCreate(BaseModel):
    comment: str

class TaskCommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime
    user_name: str = None
    
    model_config = {"from_attributes": True}
