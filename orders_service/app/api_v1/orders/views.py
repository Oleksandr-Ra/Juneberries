from fastapi import APIRouter

router = APIRouter(tags=['Orders'])


@router.get('/orders',)
async def get_orders():
    pass


@router.post('/orders',)
async def create_order():
    pass


@router.get('/orders/{id}',)
async def get_order():
    pass


@router.put('/orders/{id}',)
async def update_order():
    pass


@router.delete('/orders/{id}',)
async def delete_order():
    pass
