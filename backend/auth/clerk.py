"""
Clerk JWT verification.

How Clerk auth works at the backend:
  1. User signs in on the frontend via Clerk.
  2. Clerk issues a signed JWT (RS256) to the frontend.
  3. Frontend attaches it as `Authorization: Bearer <token>` on protected requests.
  4. We verify the JWT here using Clerk's public keys (JWKS), without ever calling
     Clerk's API at request time — verification is fully local once keys are cached.

JWKS caching:
  Clerk's public keys are fetched once and cached in memory for 1 hour (_JWKS_TTL).
  On a cache miss for a specific key ID (kid), we re-fetch once to handle key rotation
  before giving up. This means normal operation is zero network calls per request.
"""

import time

import httpx
import jwt

from shared.config import settings

_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0
_JWKS_TTL = 3600  # 1 hour


def _jwks_url() -> str:
    return f"{settings.clerk_issuer}/.well-known/jwks.json"


async def _get_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at
    if not settings.clerk_issuer:
        raise RuntimeError("CLERK_ISSUER is not set")
    if _jwks_cache and (time.monotonic() - _jwks_fetched_at) < _JWKS_TTL:
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        resp = await client.get(_jwks_url())
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_fetched_at = time.monotonic()
        return _jwks_cache


async def verify_token(token: str) -> tuple[str, str | None]:
    """
    Verify a Clerk JWT. Returns (clerk_user_id, email).

    clerk_user_id is the `sub` claim — Clerk's own user ID (e.g. "user_abc123").
    This is only used to look up or create our internal user record; it is never
    used as a primary key for any business data.

    Raises jwt.PyJWTError on invalid/expired token.
    """
    jwks = await _get_jwks()
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    # Find the matching public key by kid. Re-fetch once on miss to handle
    # the case where Clerk has rotated keys since our last fetch.
    key_data = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if key_data is None:
        global _jwks_cache
        _jwks_cache = None
        jwks = await _get_jwks()
        key_data = next((k for k in jwks["keys"] if k["kid"] == kid), None)

    if key_data is None:
        raise jwt.InvalidKeyError(f"No key found for kid={kid}")

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
    # verify_aud=False: Clerk JWTs don't include an audience claim by default.
    payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=settings.clerk_issuer,
        options={"verify_aud": False},
    )
    return payload["sub"], payload.get("email")
