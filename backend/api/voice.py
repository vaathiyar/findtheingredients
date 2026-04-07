import json
import uuid

from fastapi import APIRouter, HTTPException
from livekit import api
from pydantic import BaseModel

from backend.config import settings
from backend.auth.deps import CurrentUserDep
from shared.constants import SESSIONS_LIMIT
from shared.db.recipes import get_recipe_by_id
from shared.db.users import count_cooking_sessions, create_cooking_session

router = APIRouter(prefix="/api/voice", tags=["voice"])


class TokenRequest(BaseModel):
    recipe_id: uuid.UUID


class TokenResponse(BaseModel):
    token: str
    livekit_url: str
    room_name: str


@router.post("/token", response_model=TokenResponse)
async def create_token(req: TokenRequest, user: CurrentUserDep) -> TokenResponse:
    if get_recipe_by_id(req.recipe_id) is None:
        raise HTTPException(status_code=404, detail=f"Recipe '{req.recipe_id}' not found")

    if count_cooking_sessions(user.id) >= SESSIONS_LIMIT:
        raise HTTPException(status_code=403, detail="Demo limit reached")

    room_name = f"sous-{uuid.uuid4().hex[:8]}"

    livekit_api = api.LiveKitAPI(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )

    await livekit_api.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="sous-chef",
            room=room_name,
            metadata=json.dumps({"recipe_id": str(req.recipe_id)}),
        )
    )

    token = (
        api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(str(user.id))
        .with_name("User")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )

    await livekit_api.aclose()

    create_cooking_session(user.id, req.recipe_id, room_name)

    return TokenResponse(
        token=token,
        livekit_url=settings.livekit_url,
        room_name=room_name,
    )
