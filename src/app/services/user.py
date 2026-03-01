from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..model.user import User
from ..model.role import Role
from ..schema.user import LoginRequest, UserCreate, UserUpdate, UserResponse
from fastapi import HTTPException, UploadFile
from ..utils.argon2 import hash_password, verify_password
from ..utils.get_image import get_image

class UserService: 
    @staticmethod
    def login(db: Session, data: LoginRequest) -> UserResponse:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise ValueError("Invalid email or password")
        
        if not verify_password(user.password, data.password):
            raise ValueError("Invalid email or password")
        
        return UserResponse.model_validate(user)
    
    @staticmethod
    def setup_form(db: Session):
        roles = db.query(Role).all()

        role_options = [
            {"value": role.id, "label": role.name}
            for role in roles   
        ]
        return {
            "roles": [
                {"value": role.id, "label": role.name}
                for role in roles
            ],
            "fields": {
                "email": {
                    "type": "string",
                    "required": True
                },
                "password": {
                    "type": "password",
                    "required": True
                },
                "role_id": {
                    "type": "select",
                    "role": role_options,
                    "required": True
                },
                "image": {
                    "type": "file",
                    "required": False
                }
            }
        }
    
    @staticmethod
    def create_user(db: Session, data, image: Optional[UploadFile]) -> UserResponse:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise ValueError("Email already exists")

        role = db.query(Role).filter(Role.id == data.role_id).first()
        if not role:
            raise ValueError("Role not found")
        
        if data.password:
            data.password = hash_password(data.password)
        else:
            raise ValueError("Password is required")
        
        if image:
            data.image = get_image(image)

        user = User(**data.dict())
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserResponse.model_validate(user)
            
    @staticmethod
    def getUserById(db: Session, id: int) -> UserResponse:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            raise ValueError("User not found")
        return UserResponse.model_validate(user)
    
    # Design pagination for get all users and limits
    @staticmethod
    def getAll(db: Session, page: int, limit: int):
        total = db.query(func.count(User.id)).scalar()

        users = (
            db.query(User)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return {
            "data": [UserResponse.model_validate(user) for user in users],
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                }
        }
            
    @staticmethod
    def update_user(db: Session, id: int, data, image: Optional[UploadFile] = None) -> UserResponse:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            raise ValueError("User not found")
        
        if data.email and data.email != user.email:
            existing_user = db.query(User).filter(User.email == data.email).first()
            if existing_user:
                raise ValueError("Email already exists")
        
        if data.role_id and data.role_id != user.role_id:
            role = db.query(Role).filter(Role.id == data.role_id).first()
            if not role:
                raise ValueError("Role not found")
        
        # Hash password if provided
        if data.password:
            data.password = hash_password(data.password)
        
        # Handle image file upload separately
        if image:
            image_path = get_image(image)
            setattr(user, 'image', image_path)

        # Update only provided fields, excluding None values
        update_data = data.dict(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        
        db.commit()
        db.refresh(user)

        return UserResponse.model_validate(user) 

    @staticmethod
    def delete_user(db: Session, id: int):
        user = db.query(User).filter(User.id == id).first()
        if not user:
            db.rollback()
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}