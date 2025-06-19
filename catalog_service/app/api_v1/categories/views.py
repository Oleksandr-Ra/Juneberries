from fastapi import APIRouter

router = APIRouter(tags=['Categories'])


@router.get('/categories',)
async def get_categories():
    pass
