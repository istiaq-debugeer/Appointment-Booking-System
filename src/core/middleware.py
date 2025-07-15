from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from dependency.auth import verify_token
from repositories.user_repo import UserRepository
from services.user_service import UserService
from core.database import get_db
from sqlalchemy.orm import Session


async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/auth/login", "/auth/register"]:
        return await call_next(request)

    token = request.cookies.get("access_token")
    if not token:
        if request.url.path.startswith("/dashboard"):
            return RedirectResponse(url="/auth/login")

    else:
        # Remove Bearer prefix if present
        if token.startswith("Bearer "):
            token = token[len("Bearer ") :]

        # Verify token
        payload = verify_token(token)
        if payload:
            db: Session = next(get_db())
            email = payload.get("sub")
            user = UserRepository(db).get_user_by_email(email)
            if user:
                request.state.user = user  # ✅ Set user in request.state

    response = await call_next(request)
    return response
