from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from ..middleware.guard.permission import PermissionGuard
from ..config.session import get_db
from ..services.user import UserService
from ..schema.user import UserCreate, UserUpdate, UserResponse

user_router = APIRouter(prefix="/users", tags=["Users"])


"""
User Routes:
    If you don't want to use Form and File for the create and update routes, 
    you can change the request body to accept JSON instead. 
    However, for file uploads, using Form and File is more appropriate. 
    If you want to keep the file upload functionality, 
    you can still use Form and File for the create and update routes while accepting other fields as JSON in the request body.

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
    # Handle UploadFile and save to disk
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