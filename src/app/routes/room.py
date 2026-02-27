from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.invoice import InvoiceService
from ..config.session import get_db    
from ..services.room import RoomService
from ..schema.query import QueryParameters
from ..schema.room import RoomUpdate, RoomCreate

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@room_router.post("/")
def create_room(db: Session = Depends(get_db), data: RoomCreate = Depends()):
    try:
        room = RoomService.create_room(db, data)
        db.commit()
        db.refresh(room)
        return room
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@room_router.post("/{room_id}/assign")
def assign_tenant(room_id: int, tenant_id: int, db: Session = Depends(get_db)):
    try:        
        tenant = RoomService.assign_tenant(db, room_id, tenant_id)
        db.commit()
        db.refresh(tenant)
        return tenant
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@room_router.put("/{room_id}")
def update_room(room_id: int, db: Session = Depends(get_db), data: RoomUpdate = Depends()):
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
    return RoomService.get_all_rooms(db, params)

@room_router.get("/{room_id}")
def get_room(room_id: int, db: Session = Depends(get_db)):
    try:
        return RoomService.get_room_by_id(db, room_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@room_router.post("/{room_id}/pay")
def mark_paid(room_id: int, invoice_id: int, amount: float, db: Session = Depends(get_db)):
    try:
        payment = InvoiceService.record_payment(db, invoice_id, amount)
        db.commit()
        db.refresh(payment)
        return {"message": "Payment recorded", "payment_id": payment.id}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@room_router.get("/reports/monthly")
def get_monthly_report(month: int, year: int, db: Session = Depends(get_db)):
    return InvoiceService.get_payment_report(db, month, year)

@room_router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
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