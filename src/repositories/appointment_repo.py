from sqlalchemy.orm import Session
from models.user import User
from typing import Optional, List


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all_users(self, skip: int = 0, limit: int = 10) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_id: int, updates: dict) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        for key, value in updates.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
