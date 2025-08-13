# app/routers/auth.py
from __future__ import annotations
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db, User, Coach
from app.core.config import settings
from app.core.jwt import create_access_token
from app.core.security import verify_password, get_password_hash
from app.deps import get_current_user_strict
from app.schemas.user import UserCreate, UserResponse, UserMini
from app.schemas.coach import CoachCreate, CoachResponse, CoachOut
from sqlalchemy import select
from app.crud import user_crud

router = APIRouter(tags=["auth"])


# ---------------------------
# Register (User)
# ---------------------------
@router.post("/register/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1) line_user_id が来ていて、既に LINE でゲストが存在 → 昇格
    if payload.line_user_id:
        u_line = await user_crud.get_by_line_user_id(db, payload.line_user_id)
        if u_line:
            # email重複チェック（自分以外）
            exists = (await db.execute(
                select(User).where(User.email == payload.email, User.user_id != u_line.user_id)
            )).scalar_one_or_none()
            if exists:
                raise HTTPException(400, "このメールアドレスは既に使われています")

            u_line.username = payload.username
            u_line.email = payload.email
            u_line.password_hash = get_password_hash(payload.password)
            u_line.usertype = payload.usertype or "user"
            u_line.profile_picture_url = payload.profile_picture_url
            u_line.bio = payload.bio
            u_line.birthday = payload.birthday
            u_line.golf_score_ave = payload.golf_score_ave
            u_line.golf_exp = payload.golf_exp
            u_line.zip_code = payload.zip_code
            u_line.state = payload.state
            u_line.address1 = payload.address1
            u_line.address2 = payload.address2
            u_line.sport_exp = payload.sport_exp
            u_line.industry = payload.industry
            u_line.job_title = payload.job_title
            u_line.position = payload.position

            await db.commit()
            await db.refresh(u_line)
            return u_line

    # 2) 通常の新規作成（既存チェック）
    u = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if u:
        raise HTTPException(400, "既に登録されたメールアドレスです")

    db_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        usertype=payload.usertype or "user",
        line_user_id=payload.line_user_id,
        profile_picture_url=payload.profile_picture_url,
        bio=payload.bio,
        birthday=payload.birthday,
        golf_score_ave=payload.golf_score_ave,
        golf_exp=payload.golf_exp,
        zip_code=payload.zip_code,
        state=payload.state,
        address1=payload.address1,
        address2=payload.address2,
        sport_exp=payload.sport_exp,
        industry=payload.industry,
        job_title=payload.job_title,
        position=payload.position,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# ---------------------------
# Register (Coach)
# ---------------------------
@router.post("/register/coach", response_model=CoachResponse, status_code=status.HTTP_201_CREATED)
async def register_coach(payload: CoachCreate, db: AsyncSession = Depends(get_db)):
    u = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    c = (await db.execute(select(Coach).where(Coach.email == payload.email))).scalar_one_or_none()
    if u or c:
        raise HTTPException(status_code=400, detail="すでに登録済みのメールアドレスです")

    db_coach = Coach(
        coachname=payload.coachname,
        email=payload.email,
        usertype=payload.usertype or "coach",
        password_hash=get_password_hash(payload.password),
        birthday=payload.birthday,
        sex=payload.sex,
        SNS_handle_instagram=payload.SNS_handle_instagram,
        SNS_handle_X=payload.SNS_handle_X,
        SNS_handle_youtube=payload.SNS_handle_youtube,
        SNS_handle_facebook=payload.SNS_handle_facebook,
        SNS_handle_tiktok=payload.SNS_handle_tiktok,
        line_user_id=payload.line_user_id,
        profile_picture_url=payload.profile_picture_url,
        bio=payload.bio,
        hourly_rate=payload.hourly_rate,
        location_id=payload.location_id,
        golf_exp=payload.golf_exp,
        certification=payload.certification,
        setting_1=payload.setting_1,
        setting_2=payload.setting_2,
        setting_3=payload.setting_3,
        lesson_rank=payload.lesson_rank,
    )
    db.add(db_coach)
    await db.commit()
    await db.refresh(db_coach)
    return db_coach


# ---------------------------
# Login (User or Coach 共通)
# ---------------------------
@router.post("/token")
async def login_any(
    form: OAuth2PasswordRequestForm = Depends(),  # username に email を入れて送る
    db: AsyncSession = Depends(get_db),
):
    email = form.username

    # Userとして認証
    u = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if u and verify_password(form.password, u.password_hash):
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token({"sub": str(u.user_id), "role": "user"}, expires)
        return {"access_token": token, "token_type": "bearer", "role": "user"}

    # Coachとして認証
    c = (await db.execute(select(Coach).where(Coach.email == email))).scalar_one_or_none()
    if c and verify_password(form.password, c.password_hash):
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token({"sub": str(c.coach_id), "role": "coach"}, expires)
        return {"access_token": token, "token_type": "bearer", "role": "coach"}

    raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")


# ---------------------------
# Me
# ---------------------------
@router.get("/me")
async def me(sub: str = Depends(get_current_user_strict), db: AsyncSession = Depends(get_db)):
    # sub は JWT の "sub"（= user_id or coach_id）
    u = (await db.execute(select(User).where(User.user_id == sub))).scalar_one_or_none()
    if u:
        return {"role": "user", "profile": UserMini.model_validate(u)}
    c = (await db.execute(select(Coach).where(Coach.coach_id == sub))).scalar_one_or_none()
    if c:
        return {"role": "coach", "profile": CoachOut.model_validate(c)}
    raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
