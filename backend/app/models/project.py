from sqlalchemy import Column, String, ForeignKey, Date, Text, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    technology_stack = Column(Text, nullable=True)  # JSON string of technologies
    team_size = Column(Integer, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User", back_populates="projects")
    statuses = relationship("Status", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    team_members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
