from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, Identity
from sqlalchemy.orm import relationship

from src.app.config.base import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, Identity(start=1), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    
    # Define a relationship to the User model
    users = relationship("User", back_populates="role", cascade="all, delete")
