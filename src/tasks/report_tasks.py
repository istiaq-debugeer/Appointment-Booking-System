# app/tasks/daily_report.py

from sqlalchemy.orm import Session
from core.database import get_db
from models.appointments import Appointment
from models.user import User
from sqlalchemy import func
from app.core.celery import celery_app


@celery_app.task
def generate_daily_report():
    db = next(get_db())

    total_appointments = db.query(Appointment).count()
    total_visits = (
        db.query(Appointment).filter(Appointment.status == "COMPLETED").count()
    )
    total_earnings = db.query(func.sum(User.consultation_fee)).scalar() or 0
    total_doctors = db.query(User).filter(User.user_type == "DOCTOR").count()

    top_doctor = (
        db.query(Appointment.doctor_id, func.count(Appointment.id).label("visit_count"))
        .group_by(Appointment.doctor_id)
        .order_by(func.count(Appointment.id).desc())
        .first()
    )

    doctor_name = None
    if top_doctor:
        doctor = db.query(User).filter(User.id == top_doctor.doctor_id).first()
        doctor_name = doctor.full_name if doctor else None

    print("Daily Report Generated")
    print(f"Total Appointments: {total_appointments}")
    print(f"Total Visits: {total_visits}")
    print(f"Total Earnings: {total_earnings}")
    print(f"Total Doctors: {total_doctors}")
    print(f"Top Doctor: {doctor_name}")
