import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, datetime, timedelta
from random import randint, uniform
from src.app.model.role import Role
from src.app.model.user import User
from src.app.model.room import Room
from src.app.model.tenant import Tenant
from src.app.model.invoice import Invoice, InvoiceStatus
from src.app.model.payment import Payment, PaymentStatus 
from src.app.utils.argon2 import hash_password


# Define Color
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def seed_data(db: Session, num_tenants: int = 10, num_rooms: int = 8):
    """
    Seeds comprehensive mock data for the simplified rental system.
    
    Model: Room ↔ Tenant ↔ Invoice ↔ Payment
    - No complex booking sessions
    - Direct tenant assignment to rooms
    - Monthly invoice generation
    - Real-time payment tracking
    
    Args:
        db: Database session
        num_tenants: Number of mock tenants to create
        num_rooms: Number of mock rooms to create
    """
    
    print(f"{bcolors.OKGREEN}🌱 Starting mock data seeding for simplified rental system...{bcolors.ENDC}")
    
    # ==================== 1. Seed Roles ====================
    if db.query(Role).count() == 0:
        roles = [
            Role(name="Admin", description="System administrator", status=True),
            Role(name="Staff", description="Property manager", status=True),
            Role(name="Tenant", description="Room renter", status=True)
        ]
        db.add_all(roles)
        db.commit()
        print(f"{bcolors.OKGREEN}✓ Created {len(roles)} roles{bcolors.ENDC}x")
    
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    staff_role = db.query(Role).filter(Role.name == "Staff").first()
    
    # ==================== 2. Seed Admin User ====================
    if db.query(User).filter(User.email == "admin@example.com").count() == 0:
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password=hash_password("admin123"),
            role_id=admin_role.id,
            image="uploads/avatars/admin.jpg"
        )
        db.add(admin)
        db.commit()
        print(f"{bcolors.OKGREEN}✓ Created admin user{bcolors.ENDC}")
    
    # ==================== 3. Seed Staff Users ====================
    staff_profiles = [
        {"name": "John Manager", "email": "john@rental.com", "avatar": "john.jpg"},
        {"name": "Emma Supervisor", "email": "emma@rental.com", "avatar": "emma.jpg"},
        {"name": "Mike Maintenance", "email": "mike@rental.com", "avatar": "mike.jpg"}
    ]
    
    staff_users = []
    for profile in staff_profiles:
        if db.query(User).filter(User.email == profile["email"]).count() == 0:
            staff = User(
                name=profile["name"],
                email=profile["email"],
                password=hash_password("staff123"),
                role_id=staff_role.id,
                image=f"uploads/avatars/{profile['avatar']}"
            )
            staff_users.append(staff)
    
    if staff_users:
        db.add_all(staff_users)
        db.commit()
        print(f"{bcolors.OKGREEN}✓ Created {len(staff_users)} staff users{bcolors.ENDC}")
    
    # ==================== 4. Seed Rooms ====================
    room_catalog = [
        {"name": "A01", "desc": "Spacious suite with king bed, balcony, city view", "price": 50},
        {"name": "A02", "desc": "Modern room with queen bed and work desk", "price": 50},
        {"name": "A03", "desc": "Comfortable double room with essential amenities", "price": 50},
        {"name": "A04", "desc": "Cozy single room perfect for solo travelers", "price": 50},
        {"name": "A05", "desc": "Large suite with multiple beds, ideal for families", "price": 50},
        {"name": "A06", "desc": "Budget-friendly room with basic facilities", "price": 50},
        {"name": "A07", "desc": "Luxury suite with separate living area", "price": 50},
        {"name": "A08", "desc": "Peaceful room overlooking the garden", "price": 50},
        {"name": "A09", "desc": "Stunning ocean views from private balcony", "price": 50},
        {"name": "A10", "desc": "Self-contained studio with kitchenette", "price": 50},
        {"name": "B01", "desc": "Elegant room with vintage decor", "price": 50},
        {"name": "B02", "desc": "Cozy room with modern decor", "price": 50},
        {"name": "B03", "desc": "Spacious suite with private balcony", "price": 50},
        {"name": "B04", "desc": "Budget-friendly room with basic amenities", "price": 50},
        {"name": "B05", "desc": "Family room with multiple beds", "price": 50},
        {"name": "B06", "desc": "Luxury suite with separate living area", "price": 50},
        {"name": "B07", "desc": "Room with stunning ocean views", "price": 50},
        {"name": "B08", "desc": "Self-contained studio with kitchenette", "price": 50},
        {"name": "B09", "desc": "Elegant room with vintage decor", "price": 50},
        {"name": "B10", "desc": "Cozy room with modern decor", "price": 50}
    ]
    
    rooms = []
    for i in range(min(num_rooms, len(room_catalog))):
        room_data = room_catalog[i]
        
        if db.query(Room).filter(Room.name == room_data["name"]).count() == 0:
            room = Room(
                name=room_data["name"],
                description=room_data["desc"],
                price=room_data["price"],
                is_available=False
            )
            rooms.append(room)
    
    if rooms:
        db.add_all(rooms)
        db.flush()  # Get IDs without committing yet
        print(f"{bcolors.OKGREEN}✓ Created {len(rooms)} rooms{bcolors.ENDC}")
    
    # ==================== 5. Seed Tenants (Direct Room Assignment) ====================
    tenant_profiles = [
        {"name": "Alice Johnson", "email": "alice.j@email.com", "phone": "012-345-6789", "id_card": "ID001234"},
        {"name": "Bob Smith", "email": "bob.s@email.com", "phone": "012-456-7890", "id_card": "ID002345"},
        {"name": "Charlie Brown", "email": "charlie.b@email.com", "phone": "012-567-8901", "id_card": "ID003456"},
        {"name": "Diana Lee", "email": "diana.l@email.com", "phone": "012-678-9012", "id_card": "ID004567"},
        {"name": "Ethan Wong", "email": "ethan.w@email.com", "phone": "012-789-0123", "id_card": "ID005678"},
        {"name": "Fiona Chen", "email": "fiona.c@email.com", "phone": "012-890-1234", "id_card": "ID006789"},
        {"name": "George Kim", "email": "george.k@email.com", "phone": "012-901-2345", "id_card": "ID007890"},
        {"name": "Hannah Park", "email": "hannah.p@email.com", "phone": "012-012-3456", "id_card": "ID008901"},
        {"name": "Isaac Tan", "email": "isaac.t@email.com", "phone": "012-123-4567", "id_card": "ID009012"},
        {"name": "Julia Nguyen", "email": "julia.n@email.com", "phone": "012-234-5678", "id_card": "ID010123"},
        {"name": "Kevin Lim", "email": "kevin.l@email.com", "phone": "012-345-6780", "id_card": "ID011234"},
        {"name": "Lisa Wong", "email": "lisa.w@email.com", "phone": "012-456-7891", "id_card": "ID012345"},
        {"name": "Marcus Lee", "email": "marcus.l@email.com", "phone": "012-567-8902", "id_card": "ID013456"},
        {"name": "Nina Patel", "email": "nina.p@email.com", "phone": "012-678-9013", "id_card": "ID014567"},
        {"name": "Oscar Chen", "email": "oscar.c@email.com", "phone": "012-789-0124", "id_card": "ID015678"},
        {"name": "Paula Kim", "email": "paula.k@email.com", "phone": "012-890-1235", "id_card": "ID016789"},
        {"name": "Quinn Tan", "email": "quinn.t@email.com", "phone": "012-901-2346", "id_card": "ID017890"},
        {"name": "Rachel Ng", "email": "rachel.n@email.com", "phone": "012-012-3457", "id_card": "ID018901"},
        {"name": "Samuel Ho", "email": "samuel.h@email.com", "phone": "012-123-4568", "id_card": "ID019012"},
        {"name": "Tina Zhao", "email": "tina.z@email.com", "phone": "012-234-5679", "id_card": "ID020123"}
    ]
    
    # Get occupied rooms (is_available=False)
    occupied_rooms = [r for r in rooms if not r.is_available]
    tenants = []
    
    for i in range(min(num_tenants, len(tenant_profiles), len(occupied_rooms))):
        profile = tenant_profiles[i]
        room = occupied_rooms[i]
        
        # Check if room already has a tenant (1-to-1 relationship)
        existing_tenant = db.query(Tenant).filter(
            Tenant.room_id == room.id,
            Tenant.is_active == True
        ).first()
        
        if existing_tenant:
            continue
        
        # Random check-in date within last 6 months
        days_ago = randint(30, 180)
        check_in = datetime.utcnow() - timedelta(days=days_ago)
        
        tenant = Tenant(
            room_id=room.id,
            name=profile["name"],
            email=profile["email"],
            phone=profile["phone"],
            id_card=profile["id_card"],
            is_active=True,
            check_in_date=check_in,
            check_out_date=None
        )
        tenants.append(tenant)
    
    if tenants:
        db.add_all(tenants)
        db.flush()
        print(f"{bcolors.OKGREEN}✓ Created {len(tenants)} active tenants{bcolors.ENDC}")
    
    # ==================== 6. Seed Invoices (Monthly Billing) ====================
    today = date.today()
    current_month = today.replace(day=1)
    
    invoices = []
    
    # Generate invoices for each active tenant for last 3 months + current month
    for tenant in tenants:
        room = db.query(Room).filter(Room.id == tenant.room_id).first()
        if not room:
            continue
        
        # Generate invoices for past 3 months + current month
        for months_back in range(4):  # 0 = current, 1-3 = past
            invoice_date = current_month - timedelta(days=30 * months_back)
            month = invoice_date.month
            year = invoice_date.year
            
            # Skip if invoice already exists
            existing = db.query(Invoice).filter(
                Invoice.tenant_id == tenant.id,
                Invoice.month == month,
                Invoice.year == year
            ).first()
            
            if existing:
                continue
            
            # Determine invoice status based on scenario
            if months_back == 0:  # Current month
                # 50% paid, 30% pending, 20% late for testing variety
                status_roll = randint(1, 10)
                if status_roll <= 5:
                    status = InvoiceStatus.paid
                    amount_paid = room.price
                    paid_at = datetime.utcnow() - timedelta(days=randint(1, 4))
                elif status_roll <= 8:
                    status = InvoiceStatus.pending
                    amount_paid = 0
                    paid_at = None
                else:
                    status = InvoiceStatus.late
                    amount_paid = 0
                    paid_at = None
            elif months_back == 1:  # Last month
                # 80% paid, 20% late
                if randint(1, 10) <= 8:
                    status = InvoiceStatus.paid
                    amount_paid = room.price
                    paid_at = invoice_date.replace(day=randint(1, 28))
                else:
                    status = InvoiceStatus.late
                    amount_paid = 0
                    paid_at = None
            else:  # Older months - mostly paid
                status = InvoiceStatus.paid
                amount_paid = room.price
                paid_at = invoice_date.replace(day=randint(1, 28))
            
            invoice = Invoice(
                room_id=room.id,
                tenant_id=tenant.id,
                month=month,
                year=year,
                amount=room.price,
                amount_paid=amount_paid,
                due_date=invoice_date.replace(day=5),  # Due on 5th
                status=status,
                created_at=invoice_date,
                paid_at=paid_at
            )
            invoices.append(invoice)
    
    if invoices:
        db.add_all(invoices)
        db.flush()
        print(f"{bcolors.OKGREEN}✓ Created {len(invoices)} invoices{bcolors.ENDC}")
    
    # ==================== 7. Seed Payments (Linked to Invoices) ====================
    payments = []
    
    for invoice in invoices:
        if invoice.status == InvoiceStatus.paid and invoice.amount_paid > 0:
            # Create payment record for paid invoices
            payment = Payment(
                invoice_id=invoice.id,
                amount=invoice.amount_paid,
                image=f"uploads/receipts/payment_{invoice.id}_{invoice.month}{invoice.year}.jpg",
                status=PaymentStatus.completed,
                paid_at=invoice.paid_at or datetime.utcnow()
            )
            payments.append(payment)
        elif invoice.status == InvoiceStatus.pending and randint(1, 10) <= 3:
            # 30% of pending invoices have partial payments
            partial_amount = invoice.amount * uniform(0.3, 0.8)
            payment = Payment(
                invoice_id=invoice.id,
                amount=round(partial_amount, 2),
                image=f"uploads/receipts/partial_{invoice.id}.jpg",
                status=PaymentStatus.completed,
                paid_at=datetime.utcnow() - timedelta(days=randint(1, 10))
            )
            payments.append(payment)
            # Update invoice amount_paid
            invoice.amount_paid = partial_amount
    
    if payments:
        db.add_all(payments)
        db.commit()  # Final commit for all data
        print(f"{bcolors.OKGREEN}✓ Created {len(payments)} payments{bcolors.ENDC}")
    
    # ==================== Summary ====================
    print(f"\n{bcolors.OKGREEN}✅ Mock data seeding completed successfully!{bcolors.ENDC}")
    print(f"\n 📊 Database Summary:")
    print(f"   Roles:     {db.query(Role).count()}")
    print(f"   Users:     {db.query(User).count()} (admin/staff accounts)")
    print(f"   Rooms:     {db.query(Room).count()}")
    print(f"   Tenants:   {db.query(Tenant).filter(Tenant.is_active == True).count()} (active)")
    print(f"   Invoices:  {db.query(Invoice).count()}")
    print(f"   Payments:  {db.query(Payment).count()}")
    
    # Payment status breakdown
    paid_inv = db.query(Invoice).filter(Invoice.status == InvoiceStatus.paid).count()
    late_inv = db.query(Invoice).filter(Invoice.status == InvoiceStatus.late).count()
    pend_inv = db.query(Invoice).filter(Invoice.status == InvoiceStatus.pending).count()
    print(f"\n💰 Invoice Status:")
    print(f"   Paid:    {paid_inv}")
    print(f"   Late:    {late_inv} ⚠️")
    print(f"   Pending: {pend_inv}")
    
    return {
        "rooms": len(rooms),
        "tenants": len(tenants),
        "invoices": len(invoices),
        "payments": len(payments)
    }


def clear_all_data(db: Session):
    """
    Clears all data in correct order (respecting foreign keys)
    Also resets auto-increment sequences back to 1
    """
    print("🗑️  Clearing all data and resetting sequences...")
    
    # Handle cases where tables might not exist yet
    try:
        # Use TRUNCATE with CASCADE and RESTART IDENTITY to reset sequences
        # This is much faster than DELETE and resets IDs to 1
        db.execute(text("TRUNCATE TABLE payments, invoices, tenants, rooms, users, roles RESTART IDENTITY CASCADE"))
        db.commit()
        print("✓ All data cleared and IDs reset to 1")
    except Exception as e:
        db.rollback()
        print(f"⚠️  No existing data to clear (tables may not exist yet): {type(e).__name__}")


def reset_and_seed(db: Session, num_tenants: int = 20, num_rooms: int = 20):
    """
    Clears existing data and seeds fresh mock data
    """
    clear_all_data(db)
    return seed_data(db, num_tenants, num_rooms)


def seed_payment_scenarios(db: Session):
    """
    Additional seed for testing specific payment scenarios
    """
    print("🎯 Seeding edge-case payment scenarios...")
    
    # Get an active tenant for testing
    tenant = db.query(Tenant).filter(Tenant.is_active == True).first()
    if not tenant:
        print("⚠ No active tenant found for scenario seeding")
        return
    
    room = db.query(Room).filter(Room.id == tenant.room_id).first()
    
    # Scenario 1: Overdue invoice (30+ days late)
    old_invoice = Invoice(
        room_id=room.id,
        tenant_id=tenant.id,
        month=1,
        year=2024,
        amount=room.price,
        amount_paid=0,
        due_date=date(2024, 1, 5),
        status=InvoiceStatus.late,
        # created_at=date(2024, 1, 1)
    )
    db.add(old_invoice)
    
    # Scenario 2: Partial payment
    partial_invoice = Invoice(
        room_id=room.id,
        tenant_id=tenant.id,
        month=2,
        year=2024,
        amount=room.price,
        amount_paid=room.price * 0.5,
        due_date=date(2024, 2, 5),
        status=InvoiceStatus.pending,
        # created_at=date(2024, 2, 1)
    )
    db.add(partial_invoice)
    db.flush()  # Flush to get invoice IDs
    
    # Payment for partial invoice
    partial_payment = Payment(
        invoice_id=partial_invoice.id,
        amount=room.price * 0.5,
        status=PaymentStatus.completed,
        paid_at=datetime(2024, 2, 10, 14, 30)
    )
    db.add(partial_payment)
    
    db.commit()
    print("✓ Edge-case scenarios seeded")


# ==================== CLI Entry Point ====================
if __name__ == "__main__":
    from src.app.config.session import local_session, engine
    
    print("🚀 Running seed script directly...")
    
    db = local_session()
    try:
        # Reset and seed with default counts
        reset_and_seed(db, num_tenants=20, num_rooms=20)
        
        # Add edge-case scenarios
        seed_payment_scenarios(db)
        
    finally:
        db.close()
    
    print("\n✨ Seed script finished! Ready for testing. 🎉")