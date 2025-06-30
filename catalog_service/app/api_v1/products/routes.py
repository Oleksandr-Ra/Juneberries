from fastapi import APIRouter, Depends, status

from models import Product
from permissions import permission_required
from . import services
from .schemas import ProductSchema, ProductsSchema

router = APIRouter(prefix='/products', tags=['Products'])


@router.post(
    '',
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required('product_create'))],
)
async def create_product(
        product: Product = Depends(services.create_product),
):
    return product


@router.get(
    '',
    response_model=list[ProductsSchema],
    dependencies=[Depends(permission_required('products_read'))],
)
async def get_products(
        products: list[Product] = Depends(services.get_products),
):
    return products


@router.get(
    '/{product_id}',
    response_model=ProductSchema,
    dependencies=[Depends(permission_required('products_read'))],
)
async def get_product(
        product: Product = Depends(services.get_product_by_id),
):
    return product


@router.patch(
    '/{product_id}',
    response_model=ProductSchema,
    dependencies=[Depends(permission_required('product_update'))],
)
async def update_product(
        product: Product = Depends(services.update_product),
):
    return product


@router.delete(
    '/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(permission_required('product_delete')),
        Depends(services.delete_product),
    ],
)
async def delete_product():
    pass
