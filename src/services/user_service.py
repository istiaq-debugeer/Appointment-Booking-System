import os
from fastapi import UploadFile, Request
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from schemas.user_schema import DoctorProfileUpdate, UserType, UserCreate
from models.user import User
from dependency.auth import create_access_token
from repositories.user_repo import UserRepository
from services.appointemnt_service import AppointmentService
from core.config import templates


class UserService:
    def __init__(self, db):
        self.db = db
        self.repo = UserRepository(db) if db else None

    async def register_user_via_form(
        self,
        full_name: str,
        email: str,
        mobile: str,
        password: str,
        user_type: UserType,
        division: str,
        district: str,
        thana: str,
        license_number: str,
        experience_years: int,
        consultation_fee: float,
        available_start_time: list[str],
        available_end_time: list[str],
        profile_image: UploadFile,
    ):
        if len(available_start_time) != len(available_end_time):
            raise ValueError("Mismatch between start and end times.")

        available_timeslots = [
            {"start": s, "end": e}
            for s, e in zip(available_start_time, available_end_time)
        ]

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
            available_timeslots=available_timeslots,
        )

        # Handle file save
        if profile_image and profile_image.filename:
            image_path = f"templates/static/uploads/{profile_image.filename}"
            with open(image_path, "wb") as buffer:
                await profile_image.seek(0)
                buffer.write(await profile_image.read())
            user_data.profile_image = image_path

        user_model = User(**user_data.model_dump())
        self.repo.create_user(user_model)

        return RedirectResponse(url="/auth/login", status_code=303)

    def login_user_and_generate_response(self, email: str, password: str):
        user = self.repo.get_user_by_email(email)
        # if not user or not user.verify_password(password):
        #     raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(data={"sub": user.email, "id": user.id})
        redirect_url = (
            "/auth/admin/dashboard"
            if user.user_type == UserType.ADMIN
            else "/auth/dashboard"
        )

        response = RedirectResponse(url=redirect_url, status_code=303)
        response.set_cookie(
            key="access_token", value=f"Bearer {access_token}", httponly=True
        )
        return response

    def logout_user(self, request: Request):
        response = RedirectResponse(url="/auth/login", status_code=303)
        response.delete_cookie("access_token")
        request.session.clear()
        return response

    def render_user_dashboard(self, request: Request):
        user = request.state.user
        print()
        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "mobile": user.mobile,
            "user_type": user.user_type.value.upper(),
        }

        appointment_service = AppointmentService(self.db)

        if user_data.get("user_type") == UserType.PATIENT:
            bookings = appointment_service.get_appointments_by_user(user.id)
            return templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "user": user_data, "bookings": bookings},
            )

        elif user_data.get("user_type") == UserType.DOCTOR:
            appointments = appointment_service.get_appointments_by_doctor(user.id)
            return templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "user": user_data, "appointments": appointments},
            )

        elif user_data.get("user_type") == UserType.ADMIN:
            appointment_service = AppointmentService(self.db)
            users = self.repo.get_all_users()
            appointments = appointment_service.get_all_appointments()

            return templates.TemplateResponse(
                "admin_dashboard.html",
                {
                    "request": request,
                    "user": user,
                    "users": users,
                    "appointments": appointments,
                },
            )

    def rendered_admin_dashboard(self, request: Request):
        user = request.state.user

        if user.user_type != UserType.ADMIN:
            raise HTTPException(status_code=403, detail="Access denied")

        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "mobile": user.mobile,
            "user_type": user.user_type.value,
        }

        # Services
        appointment_service = AppointmentService(self.db)

        users = self.repo.get_all_users()
        appointments = appointment_service.get_all_appointments()

        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request,
                "user": user_data,
                "users": users,
                "appointments": appointments,
            },
        )

    def get_user_profile(self, request: Request):
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        user_data = {
            "full_name": user.full_name,
            "email": user.email,
            "mobile": user.mobile,
            "user_type": user.user_type.value,
            "division": user.division,
            "district": user.district,
            "thana": user.thana,
            "license_number": user.license_number,
            "experience_years": user.experience_years,
            "consultation_fee": user.consultation_fee,
        }

        return templates.TemplateResponse(
            "profile.html", {"request": request, "user": user_data}
        )

    def get_users_by_role(self, role: UserType):
        return self.repo.get_user_by_role(role)

    def update_doctor_profile(self, request: Request, data: DoctorProfileUpdate):

        user = request.state.user
        print(data.license_number)
        if len(data.start_time) != len(data.end_time):
            return templates.TemplateResponse(
                "edit_schedule.html",
                {
                    "request": request,
                    "error": "Mismatch between start and end times",
                    "user": user,
                    "timeslots": [
                        {"start": s, "end": e}
                        for s, e in zip(data.start_time, data.end_time)
                    ],
                },
            )

        available_timeslots = [
            {"start": st, "end": et} for st, et in zip(data.start_time, data.end_time)
        ]
        # Update user fields
        user.license_number = data.license_number
        user.experience_years = data.experience_years
        user.consultation_fee = data.consultation_fee
        user.available_timeslots = available_timeslots

        self.db.commit()
        self.db.refresh(user)
        return RedirectResponse(url="/auth/dashboard", status_code=303)
