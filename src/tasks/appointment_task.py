# app/tasks/reminder_emails.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.celery import celery_app
from core.database import get_db
from models.appointments import Appointment
from models.user import User
from utils.email_notifications import send_email
import asyncio


@celery_app.task
def send_appointment_reminders():
    db = next(get_db())

    tomorrow = datetime.utcnow().date() + timedelta(days=1)

    appointments = (
        db.query(Appointment)
        .filter(
            func.date(Appointment.appointment_time) == tomorrow,
            Appointment.status == "CONFIRMED",
        )
        .all()
    )

    for appt in appointments:
        patient = db.query(User).filter(User.id == appt.patient_id).first()
        doctor = db.query(User).filter(User.id == appt.doctor_id).first()

        if patient and doctor:
            subject = "Appointment Reminder"
            body = (
                f"Hello {patient.full_name},\n\n"
                f"This is a reminder for your appointment with Dr. {doctor.full_name} on "
                f"{appt.appointment_time.strftime('%Y-%m-%d %H:%M')}.\n\n"
                "Please be on time.\n\nThank you!"
            )
            try:
                asyncio.run(
                    send_email(to_address=patient.email, subject=subject, body=body)
                )
                print(f" Reminder sent to {patient.email}")
            except Exception as e:
                print(f"Failed to send to {patient.email}: {e}")
