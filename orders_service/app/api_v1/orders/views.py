from fastapi import APIRouter

router = APIRouter(tags=['Orders'])


@router.post('/orders',)
async def create_order():
    pass


@router.get('/orders/{id}',)
async def get_order():
    pass


@router.patch('/orders/{id}',)
async def update_order_status():
    pass


@router.delete('/orders/{id}',)
async def delete_order():
    pass
