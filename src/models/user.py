from sqlalchemy import JSON, Column, String, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB

from core.base_models import AbstractModel
from sqlalchemy import Enum
import enum


class UserType(enum.Enum):

    PATIENT = "Patient"
    DOCTOR = "Doctor"
    ADMIN = "Admin"


class User(AbstractModel):
    __tablename__ = "users"

    full_name = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    mobile = Column(String(28), nullable=False)  # +88 followed by 11 digits
    password = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    division = Column(String(100))
    district = Column(String(100))
    thana = Column(String(100))
    profile_image = Column(String(1028))
    license_number = Column(String(50), nullable=True)
    experience_years = Column(Integer, nullable=True)
    consultation_fee = Column(Float, nullable=True)
    available_timeslots = Column(
        JSON, nullable=True
    )  # e.g., [{"start": "10:00", "end": "11:00"}]
