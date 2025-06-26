from fastapi import APIRouter

from config import settings
from .categories.routes import router as categories_router
from .products.routes import router as products_router

router = APIRouter(prefix=settings.api_v1_prefix)
router.include_router(categories_router)
router.include_router(products_router)
