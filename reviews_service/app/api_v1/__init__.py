from fastapi import APIRouter

from config import settings
from .reviews.views import router as reviews_router

router = APIRouter(prefix=settings.api_v1_prefix)
router.include_router(reviews_router)
