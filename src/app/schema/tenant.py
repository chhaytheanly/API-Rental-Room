from pydantic import BaseModel, Field
from typing import Optional

class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, email=True)
    phone: Optional[str] = Field(None, max_length=50)
    id_card: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True
        
class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, email=True)
    phone: Optional[str] = Field(None, max_length=50)
    id_card: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True

class TenantAssign(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, email=True)
    phone: Optional[str] = Field(None, max_length=50)
    id_card: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True  