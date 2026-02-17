from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    can_create_projects = Column(Boolean, default=False)  # Requires approval
    
    projects = relationship("Project", back_populates="owner")
    assigned_tasks = relationship("Task", back_populates="assigned_user")
    project_memberships = relationship("ProjectMember", back_populates="user")
    task_comments = relationship("TaskComment", back_populates="user")
    access_requests_sent = relationship("AccessRequest", foreign_keys="AccessRequest.requester_id", back_populates="requester")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
