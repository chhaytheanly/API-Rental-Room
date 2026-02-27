from sqlalchemy.orm import Session
from ...model.room import Room

class bcolors:
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'  

def seed_rooms(db: Session, num_rooms: int = 20):
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
    