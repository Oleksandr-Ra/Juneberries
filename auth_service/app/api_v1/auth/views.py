from fastapi import APIRouter

router = APIRouter(tags=['Authentication'])


@router.post('/auth/register',)
async def register():
    pass


@router.post('/auth/login',)
async def login():
    pass


@router.get('/auth/me',)
async def current_user_info():
    pass


@router.post('/auth/refresh',)
async def refresh():
    pass
