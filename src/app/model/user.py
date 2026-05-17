from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, Identity
from sqlalchemy.orm import relationship

from src.app.config.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, Identity(start=1), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    image = Column(String(255), nullable=True)
    
    # Foreign key to the Role model
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users", cascade="all, delete")
