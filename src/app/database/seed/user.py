from sqlalchemy.orm import Session
from app.model.user import User
from app.model.role import Role
from app.utils.argon2 import hash_password

# Define the print color for better visibility
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

def seed_users(db: Session):
    existing = db.query(User).count()
    if existing > 0:
        print(f"{bcolors.WARNING}Users already seeded.{bcolors.ENDC}")
        return

    admin_role = db.query(Role).filter(Role.name == "Admin").first()

    if not admin_role:
        print("Admin role not found. Seed roles first.")
        return

    admin_user = User(
        name="LY Chhaythean",
        email="chhaytheanly@gmail.com",
        password=hash_password("admin@2026"),
        role_id=admin_role.id,
        image = "uploads/images/ChhayTheanLY.jpg"
    )

    db.add(admin_user)
    db.commit()

    print(f"{bcolors.OKGREEN}Users seeded successfully.{bcolors.ENDC}")