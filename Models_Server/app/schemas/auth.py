
from pydantic import BaseModel


class CurrentUser(BaseModel):
    user_id: int
    payload: dict
    access_token: str