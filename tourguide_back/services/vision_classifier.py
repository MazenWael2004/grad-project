
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import base64

load_dotenv(".env.local")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def classify_landmark(image_path: str):

    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
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
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    )

    try:
        content = response.choices[0].message.content
        return json.loads(content)

    except Exception:
        return {
            "landmark": "Unknown",
            "description": getattr(response, 'text', 'Unknown error'),
            "confidence": 0.0,
        }