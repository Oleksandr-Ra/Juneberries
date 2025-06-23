from fastapi import APIRouter, Depends, status

from models import Product
from . import services
from .schemas import ProductSchema, ProductsSchema

router = APIRouter(prefix='/products', tags=['Products'])


@router.post('', response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: Product = Depends(services.create_product),
):
    return product


@router.get('', response_model=list[ProductsSchema])
async def get_products(
        products: list[Product] = Depends(services.get_products),
):
    return products


@router.get('/{id}', response_model=ProductSchema)
async def get_product(
        product: Product = Depends(services.get_product_by_id),
):
    return product


@router.patch('/{id}', response_model=ProductSchema)
async def update_product(
        product: Product = Depends(services.update_product),
):
    return product


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(services.delete_product)])
async def delete_product():
    pass
