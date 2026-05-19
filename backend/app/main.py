from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import (
    advices,
    auth,
    cheers,
    dashboard,
    exercises,
    feed,
    goals,
    users,
    workouts,
)

settings = get_settings()

app = FastAPI(title="FitLog API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(cheers.router)
app.include_router(advices.router)
app.include_router(users.router)
app.include_router(feed.router)
app.include_router(goals.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
