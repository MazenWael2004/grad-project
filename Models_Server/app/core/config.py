from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True") == "True"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DJANGO_URL = os.getenv("DJANGO_URL", "http://localhost:8000")
CHATBOT_URL = os.getenv("CHATBOT_URL")
CHATBOT_API_KEY = os.getenv("CHATBOT_API_KEY")