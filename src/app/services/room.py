from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, and_
from datetime import datetime, date
from ..schema.room import RoomCreate, RoomUpdate, RoomDetailResponse, TenantInfo, InvoiceInfo, PaymentInfo
from ..schema.query import QueryParameters
from ..model.room import Room
from ..model.tenant import Tenant
from ..model.invoice import Invoice, InvoiceStatus
from ..model.payment import Payment, PaymentStatus
from .invoice import InvoiceService

class RoomService:
    
    @staticmethod
    def createRoom(db: Session, data: RoomCreate):
        """
        Create a new room (default: available for rent)
        """
        # Check for duplicate room name
        existing_room = db.query(Room).filter(Room.name == data.name).first()
        if existing_room:
            raise ValueError("Room with this name already exists")
        
        # Validate price
        if data.price <= 0:
            raise ValueError("Room price must be greater than 0")
        
        # Create room (is_available defaults to True)
        room = Room(
            name=data.name,
            description=data.description,
            price=data.price,
            is_available=data.is_available if hasattr(data, 'is_available') else True
        )
        
        db.add(room)
        db.commit()
        db.refresh(room)
        
        return room
    
    @staticmethod
    def getAllRooms(db: Session, query_params: QueryParameters):
        """
        Get all rooms with real-time tenant & payment status
        """
        # Build base query
        query = db.query(Room)
        
        # Apply Search (OR logic for name OR description)
        if query_params.search:
            search_filter = or_(
                Room.name.ilike(f"%{query_params.search}%"),
                Room.description.ilike(f"%{query_params.search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count (after search filter)
        total = query.count()
        
        # Apply ordering (required for consistent pagination)
        query = query.order_by(Room.id)
        
        # Apply eager loading for tenant & invoices
        query = query.options(
            selectinload(Room.tenant),
            selectinload(Room.invoices)
        )
        
        # Apply pagination
        offset = (query_params.page - 1) * query_params.limit
        rooms = query.offset(offset).limit(query_params.limit).all()
        
        # Build response with real-time status
        room_responses = []
        current_month = date.today().replace(day=1)
        
        for room in rooms:
            # Determine room status
            if room.is_available:
                status = "available"
                tenant_info = None
                payment_status = None
                amount_due = 0
                due_date = None
                current_invoice = None
            else:
                status = "occupied"
                tenant_info = TenantInfo.from_orm(room.tenant) if room.tenant else None
                
                # Find current month invoice
                current_invoice = None
                if room.tenant and room.tenant.is_active:
                    current_invoice = next(
                        (inv for inv in room.invoices 
                         if inv.year == current_month.year and inv.month == current_month.month),
                        None
                    )
                
                # Determine payment status
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
            
            # Get latest payment if exists
            latest_payment = None
            if current_invoice and current_invoice.payments:
                completed_payments = [p for p in current_invoice.payments if p.status == PaymentStatus.completed]
                if completed_payments:
                    latest_payment_orm = max(completed_payments, key=lambda p: p.paid_at)
                    latest_payment = PaymentInfo.from_orm(latest_payment_orm)
            
            room_responses.append(
                RoomDetailResponse(
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
                    updated_at=room.updated_at.isoformat() if room.updated_at else None
                )
            )
        
        # Calculate summary stats
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
    def getRoomById(db: Session, room_id: int):
        """
        Get single room with full details
        """
        room = db.query(Room).options(
            selectinload(Room.tenant),
            selectinload(Room.invoices)
        ).filter(Room.id == room_id).first()
        
        if not room:
            raise ValueError("Room not found")
        
        return RoomDetailResponse.from_orm(room)
    
    @staticmethod
    def updateRoom(db: Session, room_id: int, data: RoomUpdate):
        """
        Update room details
        """
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        # Update only provided fields
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(room, key, value)
        
        room.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(room)
        
        return RoomDetailResponse.from_orm(room)
    
    @staticmethod
    def deleteRoom(db: Session, room_id: int):
        """
        Delete room (only if no active tenant)
        """
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        # Prevent deletion if room has active tenant
        if not room.is_available:
            raise ValueError("Cannot delete room with active tenant. Remove tenant first.")
        
        db.delete(room)
        db.commit()
        
        return {"message": "Room deleted successfully"}
    
    @staticmethod
    def assignTenant(db: Session, room_id: int, tenant_data: dict):
        """
        Assign tenant to room → Room becomes occupied → Start invoicing
        """
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        if not room.is_available:
            raise ValueError("Room is already occupied")
        
        # Validate tenant data
        if not tenant_data.get("name"):
            raise ValueError("Tenant name is required")
        
        # Create tenant
        tenant = Tenant(
            room_id=room_id,
            name=tenant_data["name"],
            email=tenant_data.get("email"),
            phone=tenant_data.get("phone"),
            id_card=tenant_data.get("id_card"),
            is_active=True,
            check_in_date=datetime.utcnow()
        )
        
        # Mark room as occupied
        room.is_available = False
        room.updated_at = datetime.utcnow()
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        db.refresh(room)
        
        # Generate first invoice immediately
        InvoiceService.generate_invoice(db, tenant.id, room_id, date.today())
        
        return tenant
    
    @staticmethod
    def removeTenant(db: Session, tenant_id: int):
        """
        Remove tenant from room → Room becomes available → Stop invoicing
        """
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")
        
        # Update tenant status
        tenant.is_active = False
        tenant.check_out_date = datetime.utcnow()
        tenant.updated_at = datetime.utcnow()
        
        # Mark room as available
        room = db.query(Room).filter(Room.id == tenant.room_id).first()
        if room:
            room.is_available = True
            room.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(tenant)
        db.refresh(room)
        
        return tenant
    
    @staticmethod
    def getRoomPaymentHistory(db: Session, room_id: int, months: int = 6):
        """
        Get payment history for a room (last N months)
        """
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        # Get invoices for last N months
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
                "amount": invoice.amount,
                "amount_paid": invoice.amount_paid,
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