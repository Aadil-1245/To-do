from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.mixins import TimestampMixin

class AccessRequest(Base, TimestampMixin):
    __tablename__ = "access_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # For project join requests
    request_type = Column(String, default="create_project")  # create_project or join_project
    reason = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected
    
    requester = relationship("User", foreign_keys=[requester_id], back_populates="access_requests_sent")
    approver = relationship("User", foreign_keys=[approver_id])
    project = relationship("Project", foreign_keys=[project_id])
