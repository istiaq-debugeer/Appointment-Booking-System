from sqlalchemy.orm import Session
from models.appointments import Appointment, AppointmentStatus
from typing import List, Optional

class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_appointment(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        return appointment

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_appointments_by_user(self, user_id: int) -> List[Appointment]:
        return self.db.query(Appointment).filter(
            (Appointment.patient_id == user_id) | (Appointment.doctor_id == user_id)
        ).all()
    
    def get_appointments_by_doctor(self, doctor_id: int) -> List[Appointment]:
        query = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id)
        print(f"Query: {query}")
        results = query.all()
        print(f"Found {len(results)} appointments for doctor ID {doctor_id}")
        return results
    
    def get_all_appointments(self) -> List[Appointment]:
        return self.db.query(Appointment).all()

    def update_appointment_status(self, appointment_id: int, status: AppointmentStatus) -> Optional[Appointment]:
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            appointment.status = status
            self.db.commit()
            self.db.refresh(appointment)
        return appointment

    def delete_appointment(self, appointment_id: int) -> None:
        appointment = self.get_appointment_by_id(appointment_id)
        if appointment:
            self.db.delete(appointment)
            self.db.commit()
