import random
from typing import Callable, List, Optional, Type

from sqlalchemy.orm import Session

from src.app.utils.color import Colors

class BaseSeeder:
    """Base class for all model seeders"""
    
    def __init__(self, db: Session, model: Type, count: int = 0):
        self.db = db
        self.model = model
        self.count = count
        self.created_count = 0

    def exists(self, **filters) -> bool:
        """Check if record exists with given filters"""
        return self.db.query(self.model).filter_by(**filters).first() is not None

    def create_one(self, factory: Callable[[], dict], skip_if_exists: bool = True, **unique_fields) -> Optional[object]:
        """Create single record using factory function"""
        if skip_if_exists and unique_fields and self.exists(**unique_fields):
            return None
        
        instance = self.model(**factory())
        self.db.add(instance)
        self.db.flush()  # Get ID without committing
        self.created_count += 1
        return instance

    def create_many(self, factory: Callable[[int], dict], skip_if_exists: bool = True, 
                   unique_field: str = "id", batch_size: int = 50) -> List[object]:
        """Create multiple records using factory function"""
        instances = []
        for i in range(self.count):
            data = factory(i)
            
            if skip_if_exists and unique_field in data:
                if self.exists(**{unique_field: data[unique_field]}):
                    continue
            
            instances.append(self.model(**data))
            
            # Batch commit for performance
            if len(instances) % batch_size == 0:
                self.db.flush()
        
        if instances:
            self.db.flush()
            self.created_count += len(instances)
        
        return instances

    def log_created(self, message: str):
        Colors.success(f"Created {self.created_count} {message}")