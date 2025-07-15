from fastapi import APIRouter, Depends, File, HTTPException, Request, Form, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.database import get_db
from services.user_service import UserService
from schemas.user_schema import UserCreate, UserUpdate, UserOut, UserType, Userlogin
from typing import List
from core.config import templates
from dependency.auth import create_access_token
from models.user import User
from services.appointemnt_service import AppointmentService

router = APIRouter(prefix="/auth", tags=["Users"])
user_route = router


@router.get("/form/register")
def show_register_form(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user_types": UserType,
        },
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
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    print("Form value user_type:", user_type)
    service = UserService(db)
    print(service)
    try:
        user_data = UserCreate(
            full_name=full_name,
            email=email,
            mobile=mobile,
            password=password,
            user_type=user_type,
            division=division,
            district=district,
            thana=thana,
            license_number=license_number,
            experience_years=experience_years,
            consultation_fee=consultation_fee,
        )

        if profile_image and profile_image.filename:
    
            image_path = f"templates/static/uploads/{profile_image.filename}"
            with open(image_path, "wb") as buffer:
                await profile_image.seek(0)
                buffer.write(await profile_image.read())

            user_data.profile_image = image_path
        created_user = service.register_user(user_data)
       

        # Redirect to login page on success
        return RedirectResponse(url="/auth/login", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": str(e)}
        )
    
@router.get("/login")
def login_response(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        auth_service = UserService(db)
        user = auth_service.login_user(email, password)
        
        
        access_token = create_access_token(data={"sub": user.email, "id": user.id})
        
        # response = RedirectResponse(url="/dashboard", status_code=303)
        if user.user_type == UserType.ADMIN:
            response = RedirectResponse(url="/admin/dashboard", status_code=303)
        else:
            response = RedirectResponse(url="/dashboard", status_code=303)

        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

        return response

    except HTTPException as e:
        return templates.TemplateResponse("login.html", {"request": request, "message": e.detail})


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = request.state.user

    # Ensure user_type is a string
    user_data = {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "mobile": user.mobile,
        "user_type": user.user_type.value  # Always use .value
    }
    service = AppointmentService(db)
    if user.user_type == UserType.PATIENT:
       
        bookings = service.get_appointments_by_user(user.id)
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user_data, "bookings": bookings})
    
    elif user.user_type == UserType.DOCTOR:
        
        appointments = service.get_appointments_by_doctor(user.id)
        
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user_data, "appointments": appointments})
    
    
@router.get("/admin/dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")

    service = UserService(db)
    appointment_service = AppointmentService(db)

    users = service.get_all_users()
    appointments = appointment_service.get_all_appointments()

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user": user,
        "users": users,
        "appointments": appointments
    })

    
# @router.post("/register", response_model=UserCreate)
# def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
#     service = UserService(db)
#     try:
#         user = service.register_user(user_data)
#         return user
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))





@router.get("/", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return UserService(db).get_all_users(skip, limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = UserService(db).update_user(user_id, user_data.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = UserService(db).delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.get("/role/{role}", response_model=List[UserOut])
def get_users_by_role(role: UserType, db: Session = Depends(get_db)):
    return UserService(db).get_user_by_role(role)


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    request.session.clear()

    return response
