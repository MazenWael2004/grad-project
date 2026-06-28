from fastapi import FastAPI
import uvicorn

from app.api.routes import router
from app.core.config import HOST, PORT, DEBUG

app = FastAPI(
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