from datetime import datetime, date, timezone
from typing import Dict, Any

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from src.app.model.invoice import Invoice, InvoiceStatus
from src.app.model.payment import PaymentStatus
from src.app.model.room import Room
from src.app.model.tenant import Tenant
from src.app.schema.query import QueryParameters
from src.app.schema.room import PaymentInfo, RoomCreate, RoomDetailResponse, RoomUpdate, TenantInfo
from src.app.services.invoice import InvoiceService

class RoomService:
    
    @staticmethod
    def _build_room_response(room: Room, current_month: date) -> RoomDetailResponse:
        """Helper method to build room response with calculated fields"""
        if room.is_available:
            status = "available"
            tenant_info = None
            payment_status = None
            amount_due = 0
            due_date = None
            current_invoice = None
            latest_payment = None
        else:
            status = "occupied"
            tenant_info = TenantInfo.model_validate(room.tenant) if room.tenant else None
            
            current_invoice = None
            if room.tenant and room.tenant.is_active:
                current_invoice = next(
                    (inv for inv in room.invoices if inv.year == current_month.year and inv.month == current_month.month),
                    None
                )
            
            if current_invoice is None:
                payment_status = "no_invoice"
                amount_due = room.price
                due_date = current_month.replace(day=5)
            elif current_invoice.status == InvoiceStatus.paid:
                payment_status = "paid"
                amount_due = 0
                due_date = current_invoice.due_date
            elif current_invoice.status == InvoiceStatus.late:
                payment_status = "late"
                amount_due = current_invoice.amount - current_invoice.amount_paid
                due_date = current_invoice.due_date
            else:
                payment_status = "pending"
                amount_due = current_invoice.amount - current_invoice.amount_paid
                due_date = current_invoice.due_date
            
            latest_payment = None
            if current_invoice and current_invoice.payments:
                completed_payments = [p for p in current_invoice.payments if p.status == PaymentStatus.completed]
                if completed_payments:
                    latest_payment_orm = max(completed_payments, key=lambda p: p.paid_at)
                    latest_payment = PaymentInfo.model_validate(latest_payment_orm)
        
        return RoomDetailResponse(
            id=room.id,
            name=room.name,
            description=room.description,
            price=room.price,
            is_available=room.is_available,
            status=status,
            tenant=tenant_info,
            payment_status=payment_status,
            amount_due=amount_due,
            due_date=due_date.isoformat() if due_date else None,
            latest_payment=latest_payment,
            current_invoice_id=current_invoice.id if current_invoice else None,
            updated_at=room.updated_at.isoformat() if room.updated_at else None
        )
    
    @staticmethod
    def create_room(db: Session, data: RoomCreate) -> Room:
        """Create a new room"""
        existing_room = db.query(Room).filter(Room.name == data.name).first()
        if existing_room:
            raise ValueError("Room with this name already exists")
        
        if data.price <= 0:
            raise ValueError("Room price must be greater than 0")
        
        room = Room(
            name=data.name,
            description=data.description,
            price=data.price,
            is_available=data.is_available if hasattr(data, 'is_available') else True
        )
        
        db.add(room)
        return room
    
    @staticmethod
    def get_all_rooms(db: Session, query_params: QueryParameters) -> Dict[str, Any]:
        """Get all rooms with real-time tenant & payment status"""
        query = db.query(Room)
        
        if query_params.search:
            search_filter = or_(
                Room.name.ilike(f"%{query_params.search}%"), 
                Room.description.ilike(f"%{query_params.search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        query = query.order_by(Room.id)
        
        query = query.options(
            selectinload(Room.tenant),
            selectinload(Room.invoices).selectinload(Invoice.payments)
        )
        
        offset = (query_params.page - 1) * query_params.limit
        rooms = query.offset(offset).limit(query_params.limit).all()
        
        current_month = date.today().replace(day=1)
        room_responses = [RoomService._build_room_response(room, current_month) for room in rooms]
        
        available_count = sum(1 for r in room_responses if r.status == "available")
        occupied_count = sum(1 for r in room_responses if r.status == "occupied")
        late_count = sum(1 for r in room_responses if r.payment_status == "late")
        paid_count = sum(1 for r in room_responses if r.payment_status == "paid")
        
        return {
            "data": room_responses,
            "meta": {
                "page": query_params.page,
                "limit": query_params.limit,
                "total": total,
                "summary": {
                    "available": available_count,
                    "occupied": occupied_count,
                    "late_payments": late_count,
                    "paid": paid_count
                }
            }
        }
    
    @staticmethod
    def get_room_by_id(db: Session, room_id: int) -> RoomDetailResponse:
        """Get single room with full details"""
        room = db.query(Room).options(
            selectinload(Room.tenant),
            selectinload(Room.invoices).selectinload(Invoice.payments)
        ).filter(Room.id == room_id).first()
        
        if not room:
            raise ValueError("Room not found")
        
        current_month = date.today().replace(day=1)
        return RoomService._build_room_response(room, current_month)
    
    @staticmethod
    def update_room(db: Session, room_id: int, data: RoomUpdate) -> RoomDetailResponse:
        """Update room details"""
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(room, key, value)
        
        room.updated_at = datetime.now(timezone.utc)
        return room
    
    @staticmethod
    def delete_room(db: Session, room_id: int):
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        if not room.is_available:
            raise ValueError("Cannot delete room with active tenant. Remove tenant first.")
        
        db.delete(room)
        return {"message": "Room deleted successfully"}
    
    @staticmethod
    def assign_tenant(db: Session, room_id: int, tenant_id: int) -> Tenant:
        """Assign an existing tenant to a room"""
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        # Check if any tenant (active or inactive) is currently linked to this room
        conflicting_tenant = db.query(Tenant).filter(
            Tenant.room_id == room_id
        ).first()
        
        if conflicting_tenant:
            if conflicting_tenant.is_active:
                raise ValueError(f"Room is already occupied by active tenant: {conflicting_tenant.name} (ID: {conflicting_tenant.id})")
            else:
                # Clear the inactive tenant's room_id to resolve conflict
                conflicting_tenant.room_id = None
                db.flush()
        
        if not room.is_available:
            # Double check - if room says not available but no active tenant, fix it
            active_tenant = db.query(Tenant).filter(
                Tenant.room_id == room_id,
                Tenant.is_active == True
            ).first()
            if not active_tenant:
                room.is_available = True
            else:
                raise ValueError(f"Room is already occupied by: {active_tenant.name}")

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")

        # Check if tenant is already in another room
        if tenant.room_id is not None and tenant.is_active:
            raise ValueError(f"Tenant is already assigned to room {tenant.room_id}. Remove them first.")
        
        # Clear any old room assignment
        if tenant.room_id is not None:
            tenant.room_id = None

        tenant.room_id = room_id
        tenant.is_active = True
        tenant.check_in_date = datetime.now(timezone.utc)
        tenant.updated_at = datetime.now(timezone.utc)
        
        room.is_available = False
        room.updated_at = datetime.now(timezone.utc)
        
        # Flush changes to database before generating invoice
        db.flush()
        
        from datetime import date
        current_month = date.today().replace(day=1)
        check_in_date_value = tenant.check_in_date.date()
        
        InvoiceService.generate_invoice(
            db, 
            tenant_id=tenant.id, 
            room_id=room_id, 
            for_date=current_month,
            is_first_invoice=True,
            check_in_date=check_in_date_value
        )

        return tenant
    
    @staticmethod
    def get_room_payment_history(db: Session, room_id: int, months: int) -> Dict[str, Any]:
        """Get payment history for a room (last N months)"""
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        from datetime import timedelta
        cutoff_date = date.today() - timedelta(days=30 * months)
        
        invoices = db.query(Invoice).filter(
            Invoice.room_id == room_id,
            Invoice.created_at >= cutoff_date
        ).order_by(Invoice.year.desc(), Invoice.month.desc()).all()
        
        history = []
        for invoice in invoices:
            history.append({
                "invoice_id": invoice.id,
                "month": invoice.month,
                "year": invoice.year,
                "amount": float(invoice.amount),
                "amount_paid": float(invoice.amount_paid),
                "status": invoice.status.value,
                "due_date": invoice.due_date.isoformat(),
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None
            })
        
        return {
            "room_id": room_id,
            "room_name": room.name,
            "total_invoices": len(history),
            "data": history
        }