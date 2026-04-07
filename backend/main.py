from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.recipes import router as recipes_router
from backend.api.users import router as users_router
from backend.api.voice import router as voice_router
from backend.config import settings
from shared.db.engine import create_tables

create_tables()

app = FastAPI(title="Sous API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes_router)
app.include_router(users_router)
app.include_router(voice_router)


@app.get("/health")
def health():
    return {"status": "ok"}
