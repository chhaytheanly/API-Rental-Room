from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.app.config.session import get_db
from src.app.middleware.guard.permission import PermissionGuard
from src.app.schema.user import UserCreate, UserResponse, UserUpdate
from src.app.services.user import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])


"""
User Routes:
    If you don't want to use Form and File for the create and update routes, 
    you can change the request body to accept JSON instead. 
    However, for file uploads, using Form and File is more appropriate. 
    If you want to keep the file upload functionality, 
    you can still use Form and File for the create and update routes while accepting other fields as JSON in the request body.

"""

"""
If you don't want to handle the FormData, You can use Base64 encoding for the image and send it as a string in the JSON body.

Example of UserCreate with Base64 image:

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> UserResponse:
        # Check the existing Users
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise ValueError("Email already exists")
        
        # Check if the Role exists or seed role first
        role = db.query(Role).filter(Role.id == data.role_id).first()
        if not role:
            raise ValueError("Role not found")
        
        if data.password:
            # Hash the password before storing it in the database
            data.password = hash_password(data.password)
        else:
            raise ValueError("Password is required")
        
        # Image is now Base64 string, no processing needed
        user = User(**data.dict())
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserResponse.model_validate(user)
"""

@user_router.post("", response_model=UserResponse, dependencies=[Depends(PermissionGuard.admin_only)])
def create_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role_id: int = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    return UserService.create_user(db, UserCreate(name=name, email=email, password=password, role_id=role_id), image)
    
@user_router.get("/setup-form")
def setup_form(db: Session = Depends(get_db)):
    return UserService.setup_form(db)
    
@user_router.get("/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    try:
        return UserService.getUserById(db, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@user_router.get("")
def get_all_users(db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    return  UserService.getAll(db, page, limit)
    
@user_router.put("/{id}", response_model=UserResponse)
def update_user(
    id: int,
    name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    role_id: int = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        user_data = UserUpdate(name=name, email=email, password=password, role_id=role_id)
        return UserService.update_user(db, id, user_data, image)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@user_router.delete("/{id}", response_model=dict)
def delete_user(id: int, db: Session = Depends(get_db)):
    try:
        return UserService.delete_user(db, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))