from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from src.app.model.invoice import Invoice
from src.app.model.room import Room
from src.app.model.tenant import Tenant
from src.app.schema.query import QueryParameters
from src.app.schema.tenant import TenantCreate

class TenantService:
    @staticmethod
    def create_tenant(db: Session, data: TenantCreate) -> Tenant:
        
        existing_tenant = db.query(Tenant).filter(Tenant.email == data.email).first()
        if existing_tenant:
            raise ValueError("Tenant with this email already exists")
        
        tenant = Tenant(name=data.name,
                        email=data.email,
                        phone=data.phone,
                        id_card=data.id_card)
        
        db.add(tenant)
        return tenant
    
    @staticmethod
    def get_tenant_by_id(db: Session, tenant_id: int) -> Tenant:
        tenant = db.query(Tenant).options(
            selectinload(Tenant.room)
            ,selectinload(Tenant.invoices).selectinload(Invoice.payments)
            ).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")
        return tenant
    
    @staticmethod
    def get_all_tenants(db: Session, query_params: QueryParameters):
        query = db.query(Tenant).options(
            selectinload(Tenant.room),
            selectinload(Tenant.invoices).selectinload(Invoice.payments)
        )
        
        if query_params.search:
            search_filter = or_(
                Tenant.name.ilike(f"%{query_params.search}%"), 
                Tenant.email.ilike(f"%{query_params.search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        query = query.order_by(Tenant.id)
        
        offset = (query_params.page - 1) * query_params.limit
        tenants = query.offset(offset).limit(query_params.limit).all()
        
        return {
            "data": tenants,
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
        }
    
    @staticmethod
    def assign_tenant(db: Session, room_id: int, tenant_data: dict) -> Tenant:
        """Assign tenant to room"""
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")
        
        if not room.is_available:
            raise ValueError("Room is already occupied")
        
        if not tenant_data.get("name"):
            raise ValueError("Tenant name is required")
        
        tenant = Tenant(
            room_id=room_id,
            name=tenant_data["name"],
            email=tenant_data.get("email"),
            phone=tenant_data.get("phone"),
            id_card=tenant_data.get("id_card"),
            is_active=True,
            check_in_date=datetime.now(timezone.utc)
        )
        
        room.is_available = False
        room.updated_at = datetime.now(timezone.utc)
        
        db.add(tenant)
        return tenant
    
    @staticmethod
    def remove_tenant(db: Session, tenant_id: int) -> Tenant:
        """Remove tenant from room"""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")
        
        # Get room_id before clearing it
        room_id = tenant.room_id
        
        # Clear tenant's room assignment
        tenant.room_id = None  # Important: Clear the room_id to allow new tenant assignment
        tenant.is_active = False
        tenant.check_out_date = datetime.now(timezone.utc)
        tenant.updated_at = datetime.now(timezone.utc)
        
        # Make room available
        if room_id:
            room = db.query(Room).filter(Room.id == room_id).first()
            if room:
                room.is_available = True
                room.updated_at = datetime.now(timezone.utc)

        return tenant
