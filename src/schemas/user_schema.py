from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum


class UserType(str, Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DoDOCTORctor"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    mobile: str
    user_type: UserType
    division: str | None = None
    district: str | None = None
    thana: str | None = None
    profile_image: str | None = None


class UserCreate(UserBase):
    password: str

    class config:
        from_orm = True


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    mobile: Optional[str] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        orm_mode = True
