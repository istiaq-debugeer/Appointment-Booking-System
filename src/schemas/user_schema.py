from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum


class UserType(str, Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    full_name: str
    email: str
    mobile: str
    user_type: UserType
    division: str | None = None
    district: str | None = None
    thana: str | None = None
    profile_image: str | None = None

    @field_validator("user_type", mode="before")
    def parse_user_type(cls, value):
        if isinstance(value, str):
            try:
                return UserType[value.upper()].value  # Converts any case to uppercase enum value
            except KeyError:
                raise ValueError(f"Invalid user_type: {value}")
        elif isinstance(value, UserType):
            return value.value  # Make sure we get the string value, not the enum object
        return value
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True  # ✅ ORM mode enabled


class UserOut(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    mobile: Optional[str] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        orm_mode = True

class Userlogin(BaseModel):
    email:str
    password:str