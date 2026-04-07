from fastapi import APIRouter
from pydantic import BaseModel

from backend.auth.deps import CurrentUserDep
from shared.constants import SESSIONS_LIMIT
from shared.db.users import count_cooking_sessions

router = APIRouter(prefix="/api/users", tags=["users"])


class UserMe(BaseModel):
    sessions_used: int
    sessions_limit: int


@router.get("/me")
def get_me(user: CurrentUserDep) -> UserMe:
    return UserMe(
        sessions_used=count_cooking_sessions(user.id),
        sessions_limit=SESSIONS_LIMIT,
    )
