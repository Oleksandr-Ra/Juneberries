from fastapi import APIRouter, Depends, status

from models import Category
from permissions import permission_required
from . import services
from .schemas import CategorySchema, CategoriesSchema

router = APIRouter(prefix='/categories', tags=['Categories'])


@router.post('', response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
@permission_required('category_create')
async def create_category(
        category: Category = Depends(services.create_category)
):
    return category


@router.get('', response_model=list[CategoriesSchema])
@permission_required('categories_read')
async def get_categories(
        categories: list[Category] = Depends(services.get_categories)
):
    return categories


@router.put('/{category_id}', response_model=CategorySchema)
@permission_required('category_update')
async def update_category(
        category: Category = Depends(services.update_category)
):
    return category


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(services.delete_category)])
@permission_required('category_delete')
async def delete_category():
    pass
