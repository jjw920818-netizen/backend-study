from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Body, HTTPException, status
from sqlalchemy import select

from auth.password import hash_password, verify_password
from database.connection import engine, get_session
from database.orm import Base, User
from request import SignUpRequest, LogInRequest
from response import UserResponse

@asynccontextmanager
async def lifespan(_):
    # 서버 시작 전, 테이블 자동 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.post(
    "/users",
    summary="회원가입 API",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,     
)
async def signup_handler(
    body: SignUpRequest = Body(...),
    session = Depends(get_session),
):
    # [1] email 중복 검사
    stmt = select(User).where(User.email == body.email)
    user = await session.scalar(stmt)

    if user:
        raise HTTPException(status_code=409, detail="email already exists")

    # [2] 새로운 유저 데이터 추가 & 비밀번호 해싱(hashing)
    new_user = User(
        email=body.email, 
        password_hash=hash_password(plain_password=body.password),
    )

    # [3] user = User(email, password) 
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user) # 데이터베이스에서 id랑 created_at 읽어옴 

    return new_user

@app.post(
    "/users/login",
    summary="로그인 API",
    status_code=status.HTTP_200_OK,
)
async def login_handler(
    body: LogInRequest = Body(...),
    session = Depends(get_session),
):
    # [1] email 사용자 조회
    stmt = select(User).where(User.email == body.email)
    user: User | None = await session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

    # [2] body.password & user.passhash 비교
    verified = verify_password(plain_password=body.password, password_hash=user.password_hash)
    if not verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    # [3] 로그인 처리
    return {"result": "ok"}