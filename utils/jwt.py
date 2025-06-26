import jwt
from datetime import datetime, timedelta
import os
from typing import Optional

# Load secret key and config from environment variables
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")  # Set in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_jwt(data: dict) -> str:
    """
    Create a JWT token with expiry.
    :param data: dictionary to encode into the token (e.g., user_id)
    :return: JWT string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt(token: str) -> Optional[dict]:
    """
    Verify a JWT token.
    :param token: JWT string
    :return: Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("JWT has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid JWT token.")
        return None
