from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import User
from app.core.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.schemas import UserLogin, UserCreate, Token, UserResponse

async def authenticate_user(session: AsyncSession, username: str, password: str) -> User:
    result = await session.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def login_user(session: AsyncSession, user_data: UserLogin) -> Token:
    user = await authenticate_user(session, user_data.username, user_data.password)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

async def create_user(session: AsyncSession, user_data: UserCreate) -> UserResponse:
    result = await session.execute(select(User).filter(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    session.add(db_user)
    await session.flush()
    await session.refresh(db_user)
    
    return UserResponse.model_validate(db_user)