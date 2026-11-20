"""Google OAuth 2.0 (Authorization Code + PKCE S256 + state + nonce), клиент конфиденциальный.

Адреса эндпоинтов из discovery-документа Google (https://accounts.google.com/.well-known/openid-configuration).
Ключи для проверки id_token берутся из JWKS Google и кэшируются.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt
from jwt.algorithms import RSAAlgorithm

from fastapi import Depends

from app.config import Settings, get_settings

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
ISSUERS = ("accounts.google.com", "https://accounts.google.com")
SCOPE = "openid email profile"

JWKS_TTL = 3600.0  # секунд
JWKS_MIN_REFETCH = 60.0  # при неизвестном kid не чаще раза в минуту


class GoogleError(Exception):
    """Любой сбой входа через Google. Текст только для логов, пользователю не показывается."""


@dataclass(frozen=True)
class GoogleProfile:
    sub: str
    email: str
    name: str | None
    picture: str | None


def pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class GoogleOAuth:
    def __init__(
        self, settings: Settings, http_factory: Callable[[], httpx.Client], jwks_cache: dict[str, Any]
    ) -> None:
        self.settings = settings
        self._http = http_factory
        self._cache = jwks_cache

    def authorization_url(self, state: str, nonce: str, code_challenge: str) -> str:
        params = {
            "client_id": self.settings.GOOGLE_CLIENT_ID,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": SCOPE,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return AUTH_ENDPOINT + "?" + urlencode(params)

    def exchange_code(self, code: str, code_verifier: str) -> str:
        """Обмен кода на токены; возвращает id_token. Access/refresh-токены не сохраняются."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.google_redirect_uri,
            "client_id": self.settings.GOOGLE_CLIENT_ID,
            "client_secret": self.settings.GOOGLE_CLIENT_SECRET,
            "code_verifier": code_verifier,
        }
        try:
            with self._http() as client:
                resp = client.post(TOKEN_ENDPOINT, data=data)
        except httpx.HTTPError as exc:
            raise GoogleError(f"token endpoint unreachable: {exc.__class__.__name__}") from exc
        if resp.status_code != 200:
            raise GoogleError(f"token endpoint status {resp.status_code}")
        try:
            id_token = resp.json().get("id_token")
        except ValueError as exc:
            raise GoogleError("token endpoint returned non-JSON") from exc
        if not isinstance(id_token, str) or not id_token:
            raise GoogleError("no id_token in response")
        return id_token

    def _jwks(self, force: bool = False) -> list[dict[str, Any]]:
        now = time.monotonic()
        keys = self._cache.get("keys")
        fetched = self._cache.get("at", 0.0)
        fresh = keys is not None and now - fetched < JWKS_TTL
        if force and keys is not None and now - fetched < JWKS_MIN_REFETCH:
            return keys
        if fresh and not force:
            return keys
        try:
            with self._http() as client:
                resp = client.get(JWKS_URI)
            resp.raise_for_status()
            keys = resp.json()["keys"]
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            raise GoogleError(f"jwks unavailable: {exc.__class__.__name__}") from exc
        self._cache["keys"] = keys
        self._cache["at"] = now
        return keys

    def _key_for(self, kid: str):
        for force in (False, True):
            for jwk in self._jwks(force):
                if jwk.get("kid") == kid and jwk.get("kty") == "RSA":
                    return RSAAlgorithm.from_jwk(json.dumps(jwk))
        raise GoogleError("unknown signing key")

    def verify_id_token(self, id_token: str, nonce: str) -> GoogleProfile:
        try:
            header = jwt.get_unverified_header(id_token)
        except jwt.PyJWTError as exc:
            raise GoogleError("malformed id_token") from exc
        if header.get("alg") != "RS256" or not header.get("kid"):
            raise GoogleError("unexpected id_token alg")
        key = self._key_for(header["kid"])
        try:
            claims = jwt.decode(
                id_token,
                key,
                algorithms=["RS256"],
                audience=self.settings.GOOGLE_CLIENT_ID,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
                leeway=30,
            )
        except jwt.PyJWTError as exc:
            raise GoogleError(f"id_token rejected: {exc.__class__.__name__}") from exc
        if claims.get("iss") not in ISSUERS:
            raise GoogleError("bad issuer")
        token_nonce = claims.get("nonce")
        if not isinstance(token_nonce, str) or not hmac.compare_digest(token_nonce, nonce):
            raise GoogleError("nonce mismatch")
        verified = claims.get("email_verified")
        if verified is not True and verified != "true":
            raise GoogleError("email not verified")
        email = claims.get("email")
        sub = claims.get("sub")
        if not isinstance(email, str) or not email or not isinstance(sub, str) or not sub:
            raise GoogleError("missing email or sub")
        name = claims.get("name")
        picture = claims.get("picture")
        return GoogleProfile(
            sub=sub,
            email=email.strip().lower(),
            name=name.strip()[:100] if isinstance(name, str) and name.strip() else None,
            picture=picture[:1000] if isinstance(picture, str) and picture.startswith("https://") else None,
        )


_JWKS_CACHE: dict[str, Any] = {}


def get_google(settings: Settings = Depends(get_settings)) -> GoogleOAuth:
    """Зависимость FastAPI; тесты подменяют её, подставляя httpx.MockTransport и свой JWKS."""
    return GoogleOAuth(settings, lambda: httpx.Client(timeout=10.0), _JWKS_CACHE)
