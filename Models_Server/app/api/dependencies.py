from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

from app.core.config import DJANGO_URL
from app.core.security import verify_access_token
from app.schemas.auth import CurrentUser

security = HTTPBearer()




def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    payload = verify_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return CurrentUser(
        user_id=payload["user_id"],
        payload=payload,
        access_token=credentials.credentials,
    )


async def is_subscribed(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_URL}/api/subscriptions/is-subscribed/",
            headers={
                "Authorization": f"Bearer {current_user.access_token}",
            },
        )

    if response.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if response.status_code == 403:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription required",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to verify subscription",
        )

    data = response.json()

    if not data["subscribed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription required",
        )

    return current_user