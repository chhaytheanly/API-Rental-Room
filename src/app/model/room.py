from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String
from ..config.base import Base

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    status = Column(Boolean, nullable=True, default=True)