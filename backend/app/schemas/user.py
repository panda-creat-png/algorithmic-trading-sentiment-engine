from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_superuser: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
