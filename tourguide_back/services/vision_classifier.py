from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

load_dotenv(".env.local")

# Initialize the new Google GenAI client pointing to Vertex AI using ADC
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

def classify_landmark(image_path: str):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",
            ),
            """
You are an expert Egyptologist.

Identify the landmark shown in this image.

Possible landmarks:
- Great Pyramid of Khufu
- Pyramid of Khafre
- Pyramid of Menkaure
- Great Sphinx
- Other Giza Landmark
- Unknown

Return ONLY valid JSON:

{
  "landmark": "",
  "description": "",
  "confidence": 0.0
}
"""
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    try:
        content = response.text
        return json.loads(content)
    except Exception:
        return {
            "landmark": "Unknown",
            "description": getattr(response, 'text', 'Unknown error'),
            "confidence": 0.0,
        }