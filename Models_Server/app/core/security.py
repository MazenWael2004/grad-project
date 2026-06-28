from jose import JWTError, jwt

from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        return payload

    except JWTError:
        return None