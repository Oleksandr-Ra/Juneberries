from fastapi import APIRouter, Depends, status

from models import Category
from . import services
from .schemas import CategorySchema, CategoriesSchema

router = APIRouter(prefix='/categories', tags=['Categories'])


@router.post('', response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
        category: Category = Depends(services.create_category)
):
    return category


@router.get('', response_model=list[CategoriesSchema])
async def get_categories(
        categories: list[Category] = Depends(services.get_categories)
):
    return categories


@router.put('/{id}', response_model=CategorySchema)
async def update_category(
        category: Category = Depends(services.update_category)
):
    return category


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(services.delete_category)])
async def delete_category():
    pass
