from datetime import datetime
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from repositories.appointment_repo import AppointmentRepository
from models.appointments import Appointment, AppointmentStatus
from typing import List, Optional

from models.user import User
from repositories.user_repo import UserRepository
from schemas.appointment import AppointmentUpdate
from utils.helpers import is_time_in_slots


class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AppointmentRepository(db)
        self.user_repo = UserRepository(db)

    def create_appointment(
        self, patient_id: int, doctor_id: int, appointment_time: datetime
    ):
        doctor = self.db.query(User).filter(User.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        print(appointment_time)
        if not is_time_in_slots(appointment_time, doctor.available_timeslots or []):
            raise HTTPException(
                status_code=400,
                detail="Doctor is not available at this time. Please select a time according to the doctor's schedule.",
            )

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_time=appointment_time,
            status="PENDING",
        )
        return self.repo.create_appointment(appointment)

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        appointment = self.repo.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment

    def get_appointments_by_user(self, user_id: int) -> List[Appointment]:
        return self.repo.get_appointments_by_user(user_id)

    def get_appointments_by_doctor(self, doctor_id: int) -> List[Appointment]:
        return self.repo.get_appointments_by_doctor(doctor_id)

    def get_appointments_by_paitient(self, paitient_id: int) -> List[Appointment]:
        return self.repo.get_appointments_by_doctor(paitient_id)

    def get_all_appointments(self) -> List[Appointment]:
        return self.repo.get_all_appointments()

    def update_appointment(
        self, appointment_id: int, update_data: AppointmentUpdate
    ) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        update_data_dict = update_data.dict(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(appointment, key, value)

        self.db.commit()
        self.db.refresh(appointment)

        return appointment

    def delete_appointment(self, appointment_id: int) -> None:
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        self.db.delete(appointment)
        self.db.commit()

    def get_available_times(self, doctor_id: int):
        doctors = self.user_repo.get_user_by_id(doctor_id)
        doctors_appointment = doctors.available_timeslots
        return doctors_appointment
