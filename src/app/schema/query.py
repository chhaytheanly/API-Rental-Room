from pydantic import BaseModel
from typing import Optional

"""
Search and Pagination Logic for Rooms
"""
class QueryParameters(BaseModel):
    page: Optional[int] = 1
    limit: Optional[int] = 10
    search: Optional[str] = None