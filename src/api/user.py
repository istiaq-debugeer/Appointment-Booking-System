from fastapi import APIRouter, Depends, File, HTTPException, Request, Form, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.database import get_db
from services.user_service import UserService
from schemas.user_schema import UserCreate, UserUpdate, UserOut, UserType
from typing import List
from core.config import templates

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

        # Save image if provided
        # image_path = None
        # if profile_image:
        #     image_path = f"static/uploads/{profile_image.filename}"
        #     with open(image_path, "wb") as f:
        #         f.write(await profile_image.read())
        #     user_data.profile_image = image_path
        print(user_data)
        service.register_user(user_data)
        print("Register success, redirecting...")
        return RedirectResponse(url="/auth/login", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": str(e)}
        )


# @router.post("/register", response_model=UserCreate)
# def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
#     service = UserService(db)
#     try:
#         user = service.register_user(user_data)
#         return user
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return UserService(db).get_all_users(skip, limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserOut)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create_user(user_data)


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
