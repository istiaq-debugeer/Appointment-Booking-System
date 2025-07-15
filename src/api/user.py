from fastapi import APIRouter, Depends, Form, UploadFile, File, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import templates
from schemas.user_schema import DoctorProfileUpdate, UserCreate, UserType
from services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["Users"])

user_route = router


@router.get("/form/register")
def show_register_form(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request, "user_types": UserType}
    )


@router.post("/register")
async def handle_register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    user_type: UserType = Form(...),
    division: str = Form(None),
    district: str = Form(None),
    thana: str = Form(None),
    license_number: str = Form(None),
    experience_years: int = Form(None),
    consultation_fee: float = Form(None),
    available_start_time: list[str] = Form([]),
    available_end_time: list[str] = Form([]),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    try:
        return await service.register_user_via_form(
            full_name,
            email,
            mobile,
            password,
            user_type,
            division,
            district,
            thana,
            license_number,
            experience_years,
            consultation_fee,
            available_start_time,
            available_end_time,
            profile_image,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": str(e)}
        )


@router.get("/login")
def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    service = UserService(db)
    try:
        return service.login_user_and_generate_response(email, password)
    except HTTPException as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "message": e.detail}
        )


@router.get("/logout")
def logout(request: Request):
    service = UserService(None)
    return service.logout_user(request)


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    return UserService(db).render_user_dashboard(request)


@router.get("/admin/dashboard", name="admin_dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    return UserService(db).rendered_admin_dashboard(request)


@router.get("/profile")
def show_profile(request: Request, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_user_profile(request)


@router.post("/doctor/profile/update")
def update_doctor_profile_route(
    request: Request, data: DoctorProfileUpdate, db: Session = Depends(get_db)
):
    service = UserService(db)
    return service.update_doctor_profile(request, data)


@router.get("/doctor/profile/")
def doctor_profile_update_template(request: Request):
    user = request.state.user  # Assuming middleware sets this

    # Assuming available_timeslots is stored on the user as a list of dicts with 'start' and 'end'
    timeslots = getattr(user, "available_timeslots", [])

    return templates.TemplateResponse(
        "doctor_schedule.html",
        {
            "request": request,
            "user": user,
            "timeslots": timeslots,
            "license_number": user.license_number,
            "experience_years": user.experience_years,
            "consultation_fee": user.consultation_fee,
        },
    )
