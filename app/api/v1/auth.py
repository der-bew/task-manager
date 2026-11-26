from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.deps import DBSession
from core.security import create_access_token, get_password_hash, verify_password
from models.user import User
from schemas.token import Token
from schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data:UserCreate, db: DBSession):
    #check if a user exsistes
    email = user_data.email.strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "User already exists!"
        )
    #create a new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email = email,
        hashed_password = hashed_password,
        is_admin = False,
    )
    db.add(new_user)
    try: 
        await db.commit()
    except IntegrityError:
        await db.rollback()
        if await db.scalar(select(User.id).where(User.email == email)) is not None:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "User already exists!"
            )
        raise
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(db: DBSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    email = form_data.username.strip().lower()
    user = await db.scalar(select(User).where(User.email == email))

    if not user or not user.is_active or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect email or password"
        )
    access_token = create_access_token(user.id)
    return Token(access_token=access_token)


