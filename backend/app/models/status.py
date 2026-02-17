from sqlalchemy import Column, String, ForeignKey, Integer, UUID
from uuid import uuid4
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class Status(Base, TimestampMixin):
    __tablename__ = "statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(UUID(as_uuid=True), nullable=False, default=uuid4)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    project = relationship("Project", back_populates="statuses")
    tasks = relationship("Task", back_populates="status")
