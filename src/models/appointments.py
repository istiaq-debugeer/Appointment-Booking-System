from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Enum
from core.base_models import AbstractModel
from models.user import User
from sqlalchemy.orm import relationship
import enum


class AppointmentStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class Appointment(AbstractModel):
    __tablename__ = "appointments"

    patient_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    doctor_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    appointment_time = Column(DateTime, nullable=False)
    notes = Column(String(500))
    status = Column(
        Enum(AppointmentStatus),
        nullable=False,
        default=AppointmentStatus.PENDING,
    )

    # Relationships
    patient = relationship(
        "User", foreign_keys=[patient_id], back_populates="appointments_patient"
    )
    doctor = relationship(
        "User", foreign_keys=[doctor_id], back_populates="appointments_doctor"
    )
