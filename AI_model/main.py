from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from contextlib import asynccontextmanager
import uvicorn
import io
import traceback
import logging

logging.basicConfig(level=logging.INFO, filename="startup_error.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

# Define the model name
MODEL_NAME = "google/gemma-3n-E2B-it"



model_objects = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Loads the model on startup
    try:
        print("Loading model and tokenizer...")
        model_objects["tokenizer"] = AutoTokenizer.from_pretrained(MODEL_NAME)
        model_objects["model"] = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16,
            # if you have a good GPU change device_map to "auto"
            device_map="cpu",
            low_cpu_mem_usage=True,
        )
        print(f"Model({MODEL_NAME}) and tokenizer loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        traceback.print_exc()
        logging.exception("Error loading model and tokenizer")
        model_objects["tokenizer"] = None
        model_objects["model"] = None
    yield
    model_objects.clear()
    print("Model and tokenizer unloaded.")

app = FastAPI(lifespan=lifespan)

class TextPrompt(BaseModel):
    prompt: str

@app.post("/generate/text")
async def generate_text(prompt: TextPrompt):
    if not model_objects.get("model") or not model_objects.get("tokenizer"):
        raise HTTPException(status_code=500, detail="Model not loaded or failed to load.")

    model = model_objects["model"]
    tokenizer = model_objects["tokenizer"]
    
    try:
        input_ids = tokenizer(prompt.prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(**input_ids, max_length=100)
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during text generation: {e}")

    return {"response": response_text}

@app.post("/generate/audio")
async def generate_audio(file: UploadFile = File(...)):
    # TODO: Implement audio generation logic
    raise HTTPException(status_code=501, detail="Audio generation not implemented yet.")


@app.get("/")
def read_root():
    return {"message": f"FastAPI server for {MODEL_NAME} is running."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)