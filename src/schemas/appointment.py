from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_time: datetime
    notes: Optional[str] = None
    status: AppointmentStatus = AppointmentStatus.PENDING


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    appointment_time: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None


class AppointmentOut(AppointmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
