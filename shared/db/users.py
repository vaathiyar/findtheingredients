import uuid
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from shared.db.engine import get_session
from shared.db.models import CookingSessionRow, UserRow


def get_or_create_user(clerk_user_id: str, email: str | None) -> UserRow:
    session = get_session()
    try:
        stmt = (
            insert(UserRow)
            .values(id=uuid.uuid4(), clerk_user_id=clerk_user_id, email=email)
            .on_conflict_do_nothing(index_elements=["clerk_user_id"])
        )
        session.execute(stmt)
        session.commit()
        return session.query(UserRow).filter(UserRow.clerk_user_id == clerk_user_id).one()
    finally:
        session.close()


def count_cooking_sessions(user_id: UUID) -> int:
    session = get_session()
    try:
        return session.query(func.count(CookingSessionRow.id)).filter(CookingSessionRow.user_id == user_id).scalar()
    finally:
        session.close()


def create_cooking_session(user_id: UUID, recipe_id: UUID | None, room_name: str) -> None:
    session = get_session()
    try:
        session.add(CookingSessionRow(
            id=uuid.uuid4(),
            user_id=user_id,
            recipe_id=recipe_id,
            room_name=room_name,
        ))
        session.commit()
    finally:
        session.close()
