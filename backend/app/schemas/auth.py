import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.auth.passwords import (
    MAX_PASSWORD_LEN,
    MIN_PASSWORD_LEN,
    EmailNotValidError,
    loose_email,
    normalize_email,
)


class AccountUser(BaseModel):
    id: uuid.UUID
    display_name: str
    email: str
    provider: Literal["google", "email"]
    avatar_url: str | None = None


def _lenient_uuid(v):
    """Битый guest_user_id не ломает вход: просто игнорируется."""
    if v is None or isinstance(v, uuid.UUID):
        return v
    try:
        return uuid.UUID(str(v))
    except ValueError:
        return None


class SignupIn(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=320)
    password: str = Field(min_length=MIN_PASSWORD_LEN, max_length=MAX_PASSWORD_LEN)
    guest_user_id: uuid.UUID | None = None

    @field_validator("display_name")
    @classmethod
    def _name(cls, v: str) -> str:
        v = v.strip()
        if not v or any(ord(c) < 0x20 for c in v):
            raise ValueError("invalid display name")
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        try:
            return normalize_email(v)
        except EmailNotValidError as exc:
            raise ValueError("invalid email address") from exc

    @field_validator("guest_user_id", mode="before")
    @classmethod
    def _guest(cls, v):
        return _lenient_uuid(v)

    @model_validator(mode="after")
    def _password_not_email(self):
        if self.password.strip().lower() == self.email:
            raise ValueError("password must differ from email")
        return self


class LoginIn(BaseModel):
    email: str = Field(max_length=320)
    password: str = Field(max_length=1024)
    guest_user_id: uuid.UUID | None = None

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return loose_email(v)

    @field_validator("guest_user_id", mode="before")
    @classmethod
    def _guest(cls, v):
        return _lenient_uuid(v)
