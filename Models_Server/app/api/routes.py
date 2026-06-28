from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/api/models",
    tags=["API"],
)


@router.get("/test")
def test():
    return {
        "message": "FastAPI is working!"
    }
@router.get("/test-protected")
def test(user=Depends(get_current_user)):
    return {
        "message": "Authenticated!",
        "user": user,
    }