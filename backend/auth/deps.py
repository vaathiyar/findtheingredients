"""
FastAPI auth dependencies.

Usage — add CurrentUserDep to any endpoint that requires a signed-in user:

    @router.post("/token")
    async def create_token(req: TokenRequest, user: CurrentUserDep) -> ...:
        ...

How it works:
  1. FastAPI extracts the `Authorization: Bearer <token>` header via HTTPBearer.
  2. We verify the Clerk JWT and extract the Clerk user ID.
  3. We look up the user in our DB by clerk_user_id, creating a record on first login.
  4. The endpoint receives our internal UserRow — Clerk is fully abstracted away.

The internal UserRow.id (UUID) is the identity used everywhere in the system.
clerk_user_id only appears in the lookup step, making auth provider swaps easy.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.auth.clerk import verify_token
from shared.db.models import UserRow
from shared.db.users import get_or_create_user

_bearer = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> UserRow:
    try:
        clerk_user_id, email = await verify_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return get_or_create_user(clerk_user_id, email)


# Re-usable type alias — import this in route files instead of the raw Depends().
CurrentUserDep = Annotated[UserRow, Depends(get_current_user)]
