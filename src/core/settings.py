from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Appointment Booking System"
    debug: bool = True

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    # DB_ECHO: bool = False

    @property
    def Database_url(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


# class EmailSettings(BaseSettings):
#     # Existing settings like DATABASE_URL, etc.

#     SMTP_SERVER: str
#     SMTP_PORT: int
#     SMTP_USER: str
#     SMTP_PASSWORD: str
#     FROM_EMAIL: str

#     class Config:
#         env_file = ".env"


settings = Settings()
