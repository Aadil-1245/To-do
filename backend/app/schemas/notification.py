from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    type: str
    related_id: int = None

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    type: str
    is_read: bool
    related_id: int = None
    created_at: datetime
    
    model_config = {"from_attributes": True}
