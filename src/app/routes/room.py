from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.config.session import get_db
from src.app.schema.query import QueryParameters
from src.app.schema.room import RoomCreate, RoomUpdate
from src.app.services.room import RoomService

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])

@room_router.post("/")
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    """Create a new room"""
    try:
        room = RoomService.create_room(db, data)
        db.commit()
        db.refresh(room)
        return room
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@room_router.post("/{room_id}/assign")
def assign_tenant(room_id: int, data: dict, db: Session = Depends(get_db)):
    """Assign a tenant to a room"""
    try:        
        tenant = RoomService.assign_tenant(db, room_id, data["tenant_id"])
        db.commit()
        db.refresh(tenant)
        return tenant
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error assigning tenant: {error_detail}")  # Log to console
        raise HTTPException(status_code=500, detail=str(e))


@room_router.put("/{room_id}")
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    """Update room details"""
    try:
        room = RoomService.update_room(db, room_id, data)
        db.commit()
        db.refresh(room)
        return room
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@room_router.get("/")
def get_all_rooms(params: QueryParameters = Depends(), db: Session = Depends(get_db)):
    """List all rooms with pagination and stats"""
    return RoomService.get_all_rooms(db, params)


@room_router.get("/{room_id}")
def get_room(room_id: int, db: Session = Depends(get_db)):
    """Get single room details"""
    try:
        return RoomService.get_room_by_id(db, room_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@room_router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    """Delete a room (only if available)"""
    try:
        result = RoomService.delete_room(db, room_id)
        db.commit()
        return result
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))