from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.appointment_repo import AppointmentRepository
from models.appointments import Appointment, AppointmentStatus
from typing import List, Optional

from models.user import User
from src.utils.helpers import is_time_in_slots

class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AppointmentRepository(db)

    def create_appointment(self, patient_id: int, doctor_id: int, appointment_time: datetime):
        doctor = self.repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        if not is_time_in_slots(appointment_time, doctor.available_timeslots):
            raise HTTPException(status_code=400, detail="Doctor is not available at this time")

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_time=appointment_time,
            status="PENDING"
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

    def get_all_appointments(self) -> List[Appointment]:
        return self.repo.get_all_appointments()

    def update_appointment_status(self, appointment_id: int, status: AppointmentStatus) -> Appointment:
        appointment = self.repo.update_appointment_status(appointment_id, status)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment

    def delete_appointment(self, appointment_id: int) -> None:
        self.repo.delete_appointment(appointment_id)
