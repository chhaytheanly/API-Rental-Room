from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from src.app.database.seed.base import BaseSeeder
from src.app.model.tenant import Tenant
from src.app.model.room import Room

class TenantSeeder(BaseSeeder):
    PROFILES = [
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

    def __init__(self, db: Session, count: int = 20):
        super().__init__(db, Tenant, count)

    def seed(self, occupied_rooms: list[Room]) -> list[Tenant]:
        """Seed tenants assigned to occupied rooms"""
        tenants = []
        
        for i in range(min(self.count, len(self.PROFILES), len(occupied_rooms))):
            profile = self.PROFILES[i]
            room = occupied_rooms[i]
            
            # Skip if room already has active tenant
            if self.db.query(Tenant).filter(
                Tenant.room_id == room.id,
                Tenant.is_active == True
            ).first():
                continue
            
            # Random check-in within last 6 months
            days_ago = random.randint(30, 180)
            check_in = datetime.utcnow() - timedelta(days=days_ago)
            
            tenant = self.create_one(
                lambda: {
                    "room_id": room.id,
                    "name": profile["name"],
                    "email": profile["email"],
                    "phone": profile["phone"],
                    "id_card": profile["id_card"],
                    "is_active": True,
                    "check_in_date": check_in,
                    "check_out_date": None
                },
                skip_if_exists=False  # We already checked above
            )
            if tenant:
                tenants.append(tenant)
        
        self.log_created("active tenants")
        return tenants