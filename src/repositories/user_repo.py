from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schema import UserType
from typing import Optional, List


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_role(self, role: UserType) -> List[User]:
        return self.db.query(User).filter(User.user_type == role).all()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    def delete_user(self, user_id: int) -> None:
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
