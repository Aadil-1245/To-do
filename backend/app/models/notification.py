from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # project_assigned, task_assigned, comment_added, access_approved
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer, nullable=True)  # ID of related project/task/comment
    
    user = relationship("User", back_populates="notifications")
