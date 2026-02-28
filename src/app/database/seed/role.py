from sqlalchemy.orm import Session
from .base import BaseSeeder
from src.app.model.role import Role

class RoleSeeder(BaseSeeder):
    def __init__(self, db: Session):
        super().__init__(db, Role)

    def seed(self) -> dict:
        """Seed default roles"""
        roles_data = [
            {"name": "Admin", "description": "System administrator", "status": True},
            {"name": "Staff", "description": "Property manager", "status": True},
            {"name": "Tenant", "description": "Room renter", "status": True}
        ]
        
        for role_data in roles_data:
                if not self.exists(name=role_data["name"]):
                    self.create_one(lambda: role_data)
        
        self.log_created("roles")
        
        # Return role references for other seeders
        return {
            "admin": self.db.query(Role).filter(Role.name == "Admin").first(),
            "staff": self.db.query(Role).filter(Role.name == "Staff").first(),
            "tenant": self.db.query(Role).filter(Role.name == "Tenant").first()
        }