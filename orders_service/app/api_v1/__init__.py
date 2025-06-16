from fastapi import APIRouter

from config import settings
from .orders.views import router as orders_router

router = APIRouter(prefix=settings.api_v1_prefix)
router.include_router(orders_router)
