"""Пароли: argon2id (параметры argon2-cffi по умолчанию), rehash при смене параметров."""

from __future__ import annotations

from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from email_validator import EmailNotValidError, validate_email

MAX_PASSWORD_LEN = 128
MIN_PASSWORD_LEN = 8

_ph = PasswordHasher()


@cache
def _dummy_hash() -> str:
    """Хэш для выравнивания времени, когда пользователя нет или у него нет пароля."""
    return _ph.hash("dummy-password-for-timing-only")


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(stored_hash: str | None, password: str) -> tuple[bool, str | None]:
    """(верно?, новый хэш, если нужен rehash). Время одинаково при любом исходе."""
    if not stored_hash or len(password) > MAX_PASSWORD_LEN:
        try:
            _ph.verify(_dummy_hash(), password[:MAX_PASSWORD_LEN])
        except (VerificationError, InvalidHashError):
            pass
        return False, None
    try:
        _ph.verify(stored_hash, password)
    except (VerificationError, InvalidHashError):
        return False, None
    new_hash = _ph.hash(password) if _ph.check_needs_rehash(stored_hash) else None
    return True, new_hash


def normalize_email(raw: str) -> str:
    """Строгая проверка для регистрации. EmailNotValidError, если адрес некорректен."""
    info = validate_email(raw.strip(), check_deliverability=False)
    return info.normalized.lower()


def loose_email(raw: str) -> str:
    """Нормализация для входа: без проверки формата (некорректный email просто не найдётся)."""
    return raw.strip().lower()[:320]


__all__ = ["EmailNotValidError", "hash_password", "loose_email", "normalize_email", "verify_password"]
