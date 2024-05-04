from typing import Optional, List
from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    role: str
    username: str
    favourites: Optional[List[int]] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    new_password: Optional[str] = None


class UserForgotPassword(BaseModel):
    email: EmailStr