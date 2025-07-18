from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from repositories.user_repo import UserRepository
from .auth import verify_token


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    # Try to get token from cookie
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Token not found in cookie.",
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("id")
    user = UserRepository(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
