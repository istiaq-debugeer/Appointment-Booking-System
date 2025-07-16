from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from dependency import get_auth_user
from services.appointemnt_service import AppointmentService
from core.database import get_db
from core.config import templates  # or use direct path
from schemas.appointment import AppointmentCreate, AppointmentUpdate
from datetime import date, datetime
from services.user_service import UserService
from models.user import User
from dependency.get_auth_user import get_current_user

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
            {"request": request, "doctors": doctors, "message": e.detail},
        )


@router.get("/get-available-times")
def get_available_times(doctor_id: str, db: Session = Depends(get_db)):
    service = AppointmentService(db)
    timeslots = service.get_available_times(doctor_id)

    today = date.today().isoformat()
    formatted_times = []
    for slot in timeslots:
        if "start" in slot:
            formatted_times.append(f"{today}T{slot['start']}:00")
        if "end" in slot:
            formatted_times.append(f"{today}T{slot['end']}:00")

    return formatted_times
    # return {"appointment_time": timeslots}


@router.get("/appointments/{appointment_id}/edit")
def update_appointment_view(
    appointment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    appointment_service = AppointmentService(db)
    appointment = appointment_service.get_appointment_by_id(appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.id not in [appointment.patient_id, appointment.doctor_id]:
        raise HTTPException(
            status_code=403, detail="Not authorized to edit this appointment"
        )

    return templates.TemplateResponse(
        "edit_appointment.html", {"request": request, "appointment": appointment}
    )


@router.post("/appointments/{appointment_id}")
async def update_appointment_from_form(
    appointment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    form = await request.form()
    appointment_time_str = form.get("appointment_time")
    status = form.get("status")

    appointment_time = datetime.strptime(appointment_time_str, "%Y-%m-%dT%H:%M")

    update_data = AppointmentUpdate(date_time=appointment_time, status=status)

    appointment_service = AppointmentService(db)
    appointment_service.update_appointment(appointment_id, update_data)
    return RedirectResponse(url="/auth/dashboard", status_code=303)


@router.post("/appointments/{appointment_id}/delete")
def delete_appointment(
    appointment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment_service = AppointmentService(db)
    user_service = UserService(db)

    appointment = appointment_service.get_appointment_by_id(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment_service.delete_appointment(appointment_id)

    appointments = appointment_service.get_all_appointments()

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "user": current_user,
            "appointments": appointments,
        },
    )
