import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from core.config import settings

password_hasher = PasswordHash.recommended()

def verify_password(plain_password: str , hashed_password: str)-> bool:
    if not hashed_password:
        return False
    try: 
        return password_hasher.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False    

def get_password_hash(password:str)-> str:
    return password_hasher.hash(password)

def create_access_token(subject: str | int, expires_delta: timedelta | None = None, extra_claims: dict[str, Any] | None = None)-> str:
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES))
    
    play_load: dict[str, Any] = {"exp": expire, "iat": now, "sub": str(subject), "type": "access", "jti": str(uuid.uuid4())}

    if extra_claims:
        play_load.update(extra_claims)
    return jwt.encode(play_load, settings.SECRET_KEY, algorithm=settings.ALGORITHM)