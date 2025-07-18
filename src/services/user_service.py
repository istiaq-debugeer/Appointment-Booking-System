import os
from typing import Optional
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

    async def register_user_via_form(self, request: Request):
        form = await request.form()

        user_type = UserType(form.get("user_type"))
        full_name = form.get("full_name")
        email = form.get("email")
        mobile = form.get("mobile")
        password = form.get("password")
        division = form.get("division")
        district = form.get("district")
        thana = form.get("thana")
        license_number = form.get("license_number")
        experience_years = form.get("experience_years")
        consultation_fee = form.get("consultation_fee")
        available_start_time = form.getlist("available_start_time")
        available_end_time = form.getlist("available_end_time")
        profile_image: UploadFile = form.get("profile_image")

        print(available_end_time, available_start_time)
        # Type conversions
        experience_years = int(experience_years) if experience_years else None
        consultation_fee = float(consultation_fee) if consultation_fee else None

        # Validate timeslots for doctor
        available_timeslots = []
        if user_type == UserType.DOCTOR:
            if not all([license_number, experience_years, consultation_fee]):
                raise ValueError("Doctor-specific fields are required.")
            if len(available_start_time) != len(available_end_time):
                raise ValueError("Time slot mismatch")
            available_timeslots = [
                {"start": s, "end": e}
                for s, e in zip(available_start_time, available_end_time)
            ]
        print(available_timeslots)
        # Prepare schema
        user_data = UserCreate(
            full_name=full_name,
            email=email,
            mobile=mobile,
            password=password,
            user_type=user_type,
            division=division,
            district=district,
            thana=thana,
            license_number=license_number if user_type == UserType.DOCTOR else None,
            experience_years=experience_years if user_type == UserType.DOCTOR else None,
            consultation_fee=consultation_fee if user_type == UserType.DOCTOR else None,
            available_timeslots=available_timeslots,
        )

        # Save image
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
        if not user or not user.password == password:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(data={"sub": user.email, "id": user.id})
        redirect_url = (
            "/auth/admin/dashboard"
            if user.user_type == UserType.ADMIN
            else "/auth/dashboard"
        )

        response = RedirectResponse(url=redirect_url, status_code=303)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # set to True if using HTTPS
            samesite="lax",
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

    def update_user(self, user_id: int, user_update_data: dict) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        for key, value in user_update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user
