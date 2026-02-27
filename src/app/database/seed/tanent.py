from sqlalchemy.orm import Session
from random import randint

class bcolors:
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'  
def seed_tenants(db: Session, rooms: list, num_tenants: int = 20):
    from ...model.tenant import Tenant
    from datetime import datetime, timedelta
    
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
    