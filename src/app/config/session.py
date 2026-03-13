from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# In production, Turn Echo off
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"options": "-csearch_path=public"},
)

local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = local_session()
    
    try:
        yield db
    finally:
        db.close()