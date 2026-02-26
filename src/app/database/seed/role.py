from sqlalchemy.orm import Session
from ...model.role import Role

def seed_roles(db: Session):
    existing = db.query(Role).count()
    if existing > 0:
        print("Roles already seeded.")
        return

    roles = [
        Role(name="Admin", description="System administrator"),
        Role(name="Staff", description="System staff"),
    ]

    db.add_all(roles)
    db.commit()

    print("Roles seeded successfully.")