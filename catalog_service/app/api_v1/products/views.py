from fastapi import APIRouter

router = APIRouter(tags=['Products'])


@router.get('/products',)
async def get_products():
    pass


@router.post('/products',)
async def create_product():
    pass


@router.get('/products/{id}',)
async def get_product():
    pass


@router.put('/products/{id}',)
async def update_product():
    pass


@router.delete('/products/{id}',)
async def delete_product():
    pass
