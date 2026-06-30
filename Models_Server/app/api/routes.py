from fastapi import APIRouter, File, UploadFile, Depends
from starlette import status
from starlette.exceptions import HTTPException
from app.AI_Models.ImageClassifier import predict_image
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest
import app.state as state
from app.api.dependencies import get_current_user, is_subscribed
from app.core.config import CHATBOT_URL, CHATBOT_API_KEY
from io import BytesIO
from PIL import Image
import httpx

router = APIRouter(
    prefix="/api",
    tags=["API"],
)


@router.post("/chat/")
async def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(is_subscribed),
):
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                CHATBOT_URL,
                headers={
                    "Authorization": f"Bearer {CHATBOT_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": request.prompt,
                },
            )

        response.raise_for_status()

        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to reach chatbot service.",
        )


@router.post("/classify-image/")
async def classify(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(is_subscribed),
):
    if state.image_classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image classifier is not initialized.",
        )
    try:
        contents = await file.read()

        image = Image.open(BytesIO(contents)).convert("RGB")
        label, confidence, _ = predict_image(state.image_classifier, image)

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
