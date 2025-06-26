from fastapi import APIRouter

from config import settings
from .auth.routes import router as categories_router

router = APIRouter(prefix=settings.api_v1_prefix)
router.include_router(categories_router)
