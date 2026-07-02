from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.AI_Models.ImageClassifier import load_model
import app.state as state
import uvicorn

from app.api.routes import router
from app.core.config import HOST, PORT, DEBUG


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state.image_classifier = load_model()
        print("Model loaded.")
    except Exception as exc:
        state.image_classifier = None
        print(f"Image classifier failed to load: {exc}")

    yield

    print("Shutting down.")


app = FastAPI(
    lifespan=lifespan,
    title="HistorAI Model Server",
    version="1.0.0",
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )
