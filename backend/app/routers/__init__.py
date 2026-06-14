from fastapi import APIRouter
from app.routers import analysis, report, chat

router = APIRouter(prefix="/api/v1")
router.include_router(analysis.router)
router.include_router(report.router)
router.include_router(chat.router)
