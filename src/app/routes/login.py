import os 
from datetime import datetime, timedelta
from tokenize import Token
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..middleware.jwt_service import JWTService
from ..services.user import UserService
from ..config.session import get_db
from ..schema.user import Token, LoginRequest

load_dotenv

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

loggin_router = APIRouter(prefix="/login", tags=["Login"])

@loggin_router.post("", response_model=Token)
def login( data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = UserService.login(db, data)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token_data = {"sub": str(user.id), "role": user.role_id}
    access_token = JWTService.create_access_token(
        data=token_data,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
    )
    
    return {"access_token": access_token, "token_type": "bearer"}