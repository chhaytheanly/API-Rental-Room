from pydantic import BaseModel
from typing import Optional

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True