from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship

from src.app.config.base import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    
    # Define a relationship to the User model
    users = relationship("User", back_populates="role", cascade="all, delete")