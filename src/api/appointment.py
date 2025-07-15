from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from services.appointemnt_service import AppointmentService
from core.database import get_db
from core.config import templates  # or use direct path
from schemas.appointment import AppointmentCreate
from datetime import date, datetime
from services.user_service import UserService
from models.user import User

router = APIRouter()

appointment_route = router


@router.get("/book-appointment")
def book_appointment_form(request: Request, db: Session = Depends(get_db)):
    user_service = UserService(db)
    doctors = user_service.get_users_by_role("DOCTOR")

    return templates.TemplateResponse(
        "book_appointment.html", {"request": request, "doctors": doctors}
    )


@router.post("/book-appointment")
def book_appointment(
    request: Request,
    doctor_id: int = Form(...),
    appointment_time: datetime = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        service = AppointmentService(db)
        user = request.state.user

        service.create_appointment(
            patient_id=user.id, doctor_id=doctor_id, appointment_time=appointment_time
        )

        return RedirectResponse(url="auth/dashboard", status_code=303)

    except HTTPException as e:

        doctors = UserService(db).get_users_by_role("DOCTOR")
        return templates.TemplateResponse(
            "book_appointment.html",
            {"request": request, "doctors": doctors, "error": e.detail},
        )


@router.get("/get-available-times")
def get_available_times(doctor_id: str, db: Session = Depends(get_db)):
    service = AppointmentService(db)
    timeslots = service.get_available_times(doctor_id)

    today = date.today().isoformat()  # e.g., '2025-07-15'
    formatted_times = []
    for slot in timeslots:
        if "start" in slot:
            formatted_times.append(f"{today}T{slot['start']}:00")
        if "end" in slot:
            formatted_times.append(f"{today}T{slot['end']}:00")

    return formatted_times
    # return {"appointment_time": timeslots}
