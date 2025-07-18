from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import templates
from models.appointments import Appointment
from models.user import User
from sqlalchemy import func

router = APIRouter(prefix="/admin", tags=["Admin"])

report_router = router


@router.get("/reports")
def generate_report(request: Request, db: Session = Depends(get_db)):
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

    report = {
        "total_appointments": total_appointments,
        "total_visits": total_visits,
        "total_earnings": total_earnings,
        "total_doctors": total_doctors,
        "top_doctor": doctor_name,
    }

    return templates.TemplateResponse(
        "report.html", {"request": request, "report": report}
    )
