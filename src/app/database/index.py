from pathlib import Path
import sys

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[3]
    src_root = project_root / "src"
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    # Import all models FIRST to ensure SQLAlchemy relationships are configured
    from src.app.model.user import User
    from src.app.model.role import Role
    from src.app.model.room import Room
    from src.app.model.booking import Booking
    from src.app.model.payment import Payment
    
    from src.app.config.session import local_session
    from src.app.database.seed.seed import seed_mock_data
else:
    from ..config.session import local_session
    from .seed.seed import seed_mock_data

# Then modify your seed_all function or create a new one:
def seed_with_mock_data():
    db = local_session()
    try:
        # Option 1: Add mock data to existing data
        seed_mock_data(db, num_users=15, num_rooms=10)
        
        # Option 2: Clear everything and seed fresh
        # reset_and_seed(db, num_users=20, num_rooms=12)
        
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_with_mock_data()