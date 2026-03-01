from pydantic import BaseModel
from typing import Optional

"""
Search and Pagination Logic for Rooms
"""
class QueryParameters(BaseModel):
    page: Optional[int] = 1
    limit: Optional[int] = 100
    search: Optional[str] = None