from typing import List, Optional, Dict
from pydantic import BaseModel


class CategoryModel(BaseModel):
    id: int
    name: str


class RequestModel(BaseModel):
    requestId: int
    description: str
    location: str
    user_id: int
    like_count: Optional[int] = None
    categories: List[CategoryModel]


class RequestModelNoLike(BaseModel):
    requestId: int
    description: str
    location: str
    categories: List[int]
    user: Dict[str, str]


class RequestUpdate(BaseModel):
    description: Optional[str] = None
    location: Optional[str] = None
    categories: Optional[List[int]] = None


class UserRequests(BaseModel):
    requestsCount: int
    requests: List[RequestModel]
