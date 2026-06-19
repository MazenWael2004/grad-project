from fastapi import FastAPI, UploadFile, File
import uvicorn
import shutil
from inference import predict

app = FastAPI()

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    path = f"temp_{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    results = predict(path)

    return {
        "predictions": results
    }