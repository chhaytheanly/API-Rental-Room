from fastapi import Form
from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    name: str 
    email: str 
    password: str 
    role_id: int 
    image: Optional[str] = None
    
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        role_id: int = Form(...),
    ):
        return cls(name=name, email=email, password=password, role_id=role_id)
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None    

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