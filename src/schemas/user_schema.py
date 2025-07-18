from typing import Dict, Optional
from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum


class UserType(str, Enum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    ADMIN = "ADMIN"


from typing import List, Optional
from pydantic import BaseModel


class TimeSlot(BaseModel):
    start: str
    end: str


from pydantic import BaseModel, validator
from typing import List, Optional


class UserBase(BaseModel):
    full_name: str
    email: str
    mobile: str
    user_type: UserType

    # Optional address fields
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None

    # Doctor-specific fields
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    available_timeslots: Optional[List[Dict[str, str]]] = None

    profile_image: Optional[str] = None

    # @validator(
    #     "license_number", "experience_years", "consultation_fee", "available_timeslots"
    # )
    # def doctor_fields_required(cls, v, values):
    #     if values.get("user_type") == UserType.DOCTOR:
    #         if v is None or (isinstance(v, list) and not v):
    #             raise ValueError("This field is required for doctors")
    #     return v

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
    email: str
    password: str


class DoctorProfileUpdate(BaseModel):
    license_number: str | None = None
    experience_years: int | None = None
    consultation_fee: float | None = None
    start_time: List[str] = []
    end_time: List[str] = []
