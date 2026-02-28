from sqlalchemy.orm import Session
from sqlalchemy import text
from ...utils.color import Colors

def clear_all_data(db: Session, tables: list[str] = None):
    """
    Clears all data respecting foreign keys and resets auto-increment.
    Uses TRUNCATE for performance.
    """
    if tables is None:
        tables = ["payments", "invoices", "tenants", "rooms", "users", "roles"]
    
    try:
        # TRUNCATE with CASCADE and RESTART IDENTITY
        table_list = ", ".join(tables)
        db.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE"))
        db.commit()
        Colors.success(f"All data cleared and IDs reset for: {', '.join(tables)}")
        return True
    except Exception as e:
        db.rollback()
        Colors.warning(f"No data to clear or tables don't exist: {type(e).__name__}")
        return False