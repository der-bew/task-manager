from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.session import get_db
from models.user import User
from schemas.pagination import PaginationParams


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
DBSession = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(db: DBSession, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id : str | None = payload.get('sub')
        if user_id is None or len(user_id) > 19 or not user_id.isascii() or not user_id.isdecimal():
            raise credentials_exception
        user_id_int = int(user_id)
        if not 0 < user_id_int <= 2**63 - 1:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_admin(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."            
        )
    return current_user

AdminUser = Annotated[User, Depends(get_current_admin)]
PaginationDep = Annotated[PaginationParams, Depends()]