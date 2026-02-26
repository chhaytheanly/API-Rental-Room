from pathlib import Path
import sys

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.app.config.session import local_session
    from src.app.database.seed.role import seed_roles
    from src.app.database.seed.user import seed_users
else:
    from ..config.session import local_session
    from .seed.role import seed_roles
    from .seed.user import seed_users


def seed_all():
    db = local_session()

    try:
        print("Starting database seeding...")

        seed_roles(db)
        seed_users(db)

        print("Database seeding completed.")

    except Exception as e:
        db.rollback()
        print("Seeding failed:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_all()