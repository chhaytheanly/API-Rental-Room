from fastapi import File, Form
from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role_id: int
    image: Optional[str] = None

    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None    
    image: Optional[str] = None


class RoleNested(BaseModel):
    id: int
    name: str
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role_id: int
    image: Optional[str] = None
    role: RoleNested

    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class LoginRequest(BaseModel):
    email: str
    password: str