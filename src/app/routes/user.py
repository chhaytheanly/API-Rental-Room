from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..middleware.guard.permission import PermissionGuard
from ..config.session import get_db
from ..services.user import UserService
from ..schema.user import UserCreate, UserUpdate, UserResponse
from fastapi import Query

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("", response_model=UserResponse, dependencies=[Depends(PermissionGuard.admin_only)])
def create_user(
    data: UserCreate = Depends(UserCreate.as_form),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    try:
        return UserService.create_user(db, data, image)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@user_router.get("/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    try:
        return UserService.getUserById(db, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@user_router.get("/")
def get_all_users(db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    return  UserService.getAll(db, page, limit)
    
@user_router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    try:
        return UserService.update_user(db, id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@user_router.delete("/{id}", response_model=dict)
def delete_user(id: int, db: Session = Depends(get_db)):
    try:
        return UserService.delete_user(db, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))