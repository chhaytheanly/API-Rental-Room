from sqlalchemy.orm import Session

from src.app.database.seed.base import BaseSeeder
from src.app.model.room import Room

class RoomSeeder(BaseSeeder):
    ROOM_CATALOG = [
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

    def __init__(self, db: Session, count: int = 20):
        super().__init__(db, Room, count)

    def seed(self) -> list[Room]:
        """Seed rooms from catalog"""
        rooms = []
        for i in range(min(self.count, len(self.ROOM_CATALOG))):
            data = self.ROOM_CATALOG[i]
            if not self.exists(name=data["name"]):
                room = self.create_one(
                    lambda: {
                        "name": data["name"],
                        "description": data["desc"],
                        "price": data["price"],
                        "is_available": False  # Mark as occupied for tenant seeding
                    },
                )
                if room:
                    rooms.append(room)
        
        self.log_created("rooms")
        return rooms