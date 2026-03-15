from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
import os
from sqlalchemy.orm import Session

from src.app.config.session import get_db
from src.app.middleware.jwt_service import JWTService
from src.app.services.user import UserService

load_dotenv()

security = HTTPBearer()

class PermissionGuard:
    
    @staticmethod
    def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
        try:
            payload = JWTService.verify_token(token.credentials, secret_key=os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM").split(","))
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            user = UserService.getUserById(db, user_id)
            return user
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def admin_only(current_user=Depends(get_current_user)):
        if current_user.role.name.lower() != "admin":
            raise HTTPException(status_code=403, detail="Admin privileges required")
        return current_user

