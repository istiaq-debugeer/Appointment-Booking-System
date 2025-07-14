from sqlalchemy.orm import Session
from repositories.user_repo import UserRepository
from schemas.user_schema import UserCreate, UserOut, UserUpdate
from models.user import User
from typing import List, Optional


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> UserOut:
        data = user_data.model_dump()
        data["user_type"] = data["user_type"].value  # ✅ Convert Enum to string

        user_model = User(**data)
        created_user = self.repo.create_user(user_model)
        print(created_user)

    def get_user_by_id(self, user_id: int) -> Optional[UserOut]:
        user = self.repo.get_user_by_id(user_id)
        return UserOut.from_orm(user) if user else None

    def get_user_by_email(self, email: str) -> Optional[UserOut]:
        user = self.repo.get_user_by_email(email)
        return UserOut.from_orm(user) if user else None

    # def create_user(self, user_data: UserCreate) -> UserOut:
    #     user_model = User(**user_data.model_dump())
    #     created_user = self.repo.create_user(user_model)
    #     return UserOut.from_orm(created_user)

    def get_all_users(self, skip: int = 0, limit: int = 10) -> List[UserOut]:
        users = self.repo.get_all_users(skip, limit)
        return [UserOut.from_orm(user) for user in users]

    def update_user(self, user_id: int, updates: dict) -> Optional[UserOut]:
        updated_user = self.repo.update_user(user_id, updates)
        return UserOut.from_orm(updated_user) if updated_user else None

    def delete_user(self, user_id: int) -> bool:
        return self.repo.delete_user(user_id)
