from sqlalchemy import Column, Integer, String, ForeignKey, Text 
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class TaskComment(Base, TimestampMixin):
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")
