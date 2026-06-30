from typing import Annotated
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    prompt: Annotated[str, Field(max_length=400)]