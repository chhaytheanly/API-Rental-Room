from sqlalchemy.orm import Session
from .base import BaseSeeder
from src.app.model.user import User
from src.app.utils.argon2 import hash_password
from ...utils.color import Colors

class UserSeeder(BaseSeeder):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def seed_admin(self, role_id: int) -> User:
        """Seed admin user"""
        if not self.exists(email="admin@example.com"):
                admin = self.create_one(
                    lambda: {
                        "name": "Admin User",
                        "email": "admin@example.com",
                        "password": hash_password("admin123"),
                        "role_id": role_id,
                        "image": "uploads/avatars/admin.jpg"
                    }
                )
        Colors.success("Created admin user")
        return admin

    def seed_staff(self, role_id: int) -> list[User]:
        """Seed staff users"""
        profiles = [
            {"name": "John Manager", "email": "john@rental.com", "avatar": "john.jpg"},
            {"name": "Emma Supervisor", "email": "emma@rental.com", "avatar": "emma.jpg"},
            {"name": "Mike Maintenance", "email": "mike@rental.com", "avatar": "mike.jpg"}
        ]
        
        staff_users = []
        for profile in profiles:
            if not self.exists(email=profile["email"]):
                user = self.create_one(
                    lambda: {
                        "name": profile["name"],
                        "email": profile["email"],
                        "password": hash_password("staff123"),
                        "role_id": role_id,
                        "image": f"uploads/avatars/{profile['avatar']}"
                    },
                )
                if user:
                    staff_users.append(user)
        
        if staff_users:
            Colors.success(f"Created {len(staff_users)} staff users")
        
        return staff_users