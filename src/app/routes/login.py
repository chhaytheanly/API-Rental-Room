from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.config.config import settings
from src.app.config.logger import security_logger
from src.app.config.session import get_db
from src.app.middleware.jwt_service import JWTService
from src.app.schema.user import LoginRequest, Token
from src.app.services.user import UserService
from src.app.utils.device_tracker import DeviceTracker


loggin_router = APIRouter(prefix="/login", tags=["Login"])

@loggin_router.post("", response_model=Token)
def login( request: Request,data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = UserService.login(db, data)
        info = DeviceTracker.get_device_info(request)
        client_ip = DeviceTracker.get_client_ip(request)
        security_logger.info(f"User {user.email} logged in from IP {client_ip} with device info: {info}")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token_data = {"sub": str(user.id), "role": user.role_id}
    access_token = JWTService.create_access_token(
        data=token_data,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return {"access_token": access_token, "token_type": "bearer", "info": info}