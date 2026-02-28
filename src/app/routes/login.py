import os 
from datetime import timedelta
from tokenize import Token
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..middleware.jwt_service import JWTService
from ..services.user import UserService
from ..config.session import get_db
from ..schema.user import LoginRequest
from ..schema.user import Token
from ..config.logger import security_logger
from ..utils.device_tracker import DeviceTracker

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


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
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
    )
    
    return {"access_token": access_token, "token_type": "bearer", "info": info}