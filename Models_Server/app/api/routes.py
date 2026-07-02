from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Depends
from starlette import status
from starlette.exceptions import HTTPException
from app.AI_Models.ImageClassifier import load_model, predict_image, predict_top_k
from app.schemas.auth import CurrentUser
from app.schemas.chat import ChatRequest
from app.schemas.classifier import ReloadModelRequest, TrainingStartRequest
import app.state as state
from app.api.dependencies import get_current_user, is_subscribed, verify_internal_api_key
from app.core.config import CHATBOT_URL, CHATBOT_API_KEY
from app.services.classifier_training import (
    create_training_job,
    get_training_job,
    run_training_job,
)
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
        predictions, _ = predict_top_k(state.image_classifier, image, top_k=5)

        return {
            "label": label,
            "confidence": confidence * 100,
            "model_version": state.image_classifier.model_version,
            "predictions": [
                {
                    "label": prediction["label"],
                    "confidence": prediction["confidence"] * 100,
                }
                for prediction in predictions
            ],
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


@router.post(
    "/internal/classifier/training-runs/start",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_internal_api_key)],
)
async def start_classifier_training(
    request: TrainingStartRequest,
    background_tasks: BackgroundTasks,
):
    try:
        job = create_training_job(request.model_dump())
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    background_tasks.add_task(run_training_job, job["job_id"], request.model_dump())
    return {
        "job_id": job["job_id"],
        "status": job["status"],
    }


@router.get(
    "/internal/classifier/training-runs/{job_id}",
    dependencies=[Depends(verify_internal_api_key)],
)
async def get_classifier_training_job(job_id: str):
    job = get_training_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classifier training job not found.",
        )
    return job


@router.post(
    "/internal/classifier/model-versions/reload",
    dependencies=[Depends(verify_internal_api_key)],
)
async def reload_classifier_model(request: ReloadModelRequest):
    try:
        state.image_classifier = load_model(
            request.checkpoint_path,
            model_version=str(request.model_version_id),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "message": "Classifier model loaded.",
        "model_version": request.model_version_id,
        "class_count": len(state.image_classifier.class_names),
    }
