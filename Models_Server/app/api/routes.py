from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, is_subscribed

router = APIRouter(
    prefix="/api/models",
    tags=["API"],
)


@router.get("/test/")
async def test():
    return {
        "message": "FastAPI is working!"
    }


@router.get("/test-protected/")
async def test_protected(user=Depends(get_current_user)):
    return {
        "message": "Authenticated!",
        "user": user,
    }


@router.get("/test-restricted/")
async def test_restricted(user=Depends(is_subscribed)):
    return {
        "message": "Subscribed!",
        "user": user,
    }