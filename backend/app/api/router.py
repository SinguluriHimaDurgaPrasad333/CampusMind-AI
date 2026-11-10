from fastapi import APIRouter
from app.api.endpoints import health, chat, admin, analytics, evaluation

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(admin.router)
api_router.include_router(analytics.router)
api_router.include_router(evaluation.router)
