from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..middleware.guard.permission import PermissionGuard
from ..config.session import get_db    
from ..services.room import RoomService
from ..schema.room import RoomCreate, RoomUpdate, RoomDetailResponse
from ..schema.query import QueryParameters

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])

@room_router.get("")
def get_rooms(db: Session = Depends(get_db), query_params: QueryParameters = Depends(), dependencies = [Depends(PermissionGuard.admin_only)]):
    return RoomService.getAllRooms(db, query_params)