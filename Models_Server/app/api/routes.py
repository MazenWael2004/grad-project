from fastapi import APIRouter, File, UploadFile, Depends
from starlette import status
from starlette.exceptions import HTTPException
from app.AI_Models.ImageClassifier import predict_image
import app.state as state
from app.api.dependencies import CurrentUser, get_current_user, is_subscribed
from io import BytesIO
from PIL import Image

router = APIRouter(
    prefix="/api",
    tags=["API"],
)


@router.post("/classify-image/")
async def classify(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    try:
        contents = await file.read()

        image = Image.open(BytesIO(contents)).convert("RGB")
        label, confidence, _ = predict_image(
            state.model,
            state.preprocess,
            state.class_names,
            state.device,
            image,
        )

        return {
            "label": label,
            "confidence": confidence * 100,
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/test/")
async def test():
    return {"message": "FastAPI is working!"}


@router.get("/test-protected/")
async def test_protected(
    current_user: CurrentUser = Depends(get_current_user),
):
    return {
        "message": "Authenticated!",
        "user_id": current_user.user_id,
        "payload": current_user.payload,
    }


@router.get("/test-restricted/")
async def test_restricted(
    current_user: CurrentUser = Depends(is_subscribed),
):
    return {
        "message": "Subscribed!",
        "user_id": current_user.user_id,
        "payload": current_user.payload,
    }
