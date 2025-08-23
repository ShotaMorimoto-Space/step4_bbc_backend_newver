# app/routers/auth.py
from __future__ import annotations
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Coach
from app.core.config import settings
from app.core.jwt import create_access_token
from app.core.security import verify_password, get_password_hash
from app.deps import get_current_user_strict, get_database
from uuid import UUID
from app.schemas.user import (
    UserRegister,
    UserProfileUpdate,
    UserResponse,
    UserMini,
)
from app.schemas.coach import CoachCreate, CoachResponse, CoachOut,CoachUpdate
from sqlalchemy import select
from app.crud import user_crud

router = APIRouter(tags=["auth"])


# ---------------------------
# Register (User)
# ---------------------------
@router.post("/register/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_database)):
    u = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if u:
        raise HTTPException(400, "既に登録されたメールアドレスです")

    db_user = User(
        username=payload.username,
        email=payload.email,
        gender=payload.gender,
        birthday=payload.birthday,
        password_hash=get_password_hash(payload.password),
        usertype="user",
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserResponse.model_validate(db_user, from_attributes=True)

@router.patch("/user/{user_id}/profile", response_model=UserResponse)
async def update_user_profile(user_id: UUID, payload: UserProfileUpdate, db: AsyncSession = Depends(get_database)):
    user = (await db.execute(select(User).where(User.user_id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "ユーザーが見つかりません")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user, from_attributes=True)

# ---------------------------
# Register (Coach)
# ---------------------------
@router.post("/register/coach", response_model=CoachResponse, status_code=status.HTTP_201_CREATED)
async def register_coach(payload: CoachCreate, db: AsyncSession = Depends(get_database)):
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

@router.patch("/coach/{coach_id}/profile", response_model=CoachResponse)
async def update_coach_profile(coach_id: UUID, payload: CoachUpdate, db: AsyncSession = Depends(get_database)):
    coach = (await db.execute(select(Coach).where(Coach.coach_id == coach_id))).scalar_one_or_none()
    if not coach:
        raise HTTPException(404, "コーチが見つかりません")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(coach, key, value)

    await db.commit()
    await db.refresh(coach)

    return CoachResponse.model_validate(coach, from_attributes=True)


# ---------------------------
# Login (User or Coach 共通)
# ---------------------------
@router.post("/token")
async def login_any(
    form: OAuth2PasswordRequestForm = Depends(),  # username に email を入れて送る
    db: AsyncSession = Depends(get_database),
):
    try:
        print(f"=== ログイン試行開始 ===")
        print(f"受信したemail: {form.username}")
        print(f"パスワード長: {len(form.password) if form.password else 0}")
        
        email = form.username
        
        if not email:
            print("エラー: emailが空です")
            raise HTTPException(status_code=400, detail="メールアドレスが入力されていません")
        
        if not form.password:
            print("エラー: パスワードが空です")
            raise HTTPException(status_code=400, detail="パスワードが入力されていません")

        # Userとして認証
        print(f"Userテーブルで検索中: {email}")
        u = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
        
        if u:
            print(f"Userが見つかりました: {u.user_id}")
            print(f"パスワード検証中...")
            if verify_password(form.password, u.password_hash):
                print(f"パスワード検証成功")
                expires = timedelta(minutes=settings.access_token_expire_minutes)
                token = create_access_token({"sub": str(u.user_id), "role": "user"}, expires)
                print(f"トークン生成成功: {token[:20]}...")
                return {"access_token": token, "token_type": "bearer", "role": "user"}
            else:
                print(f"パスワード検証失敗")
        else:
            print(f"Userが見つかりませんでした: {email}")

        # Coachとして認証
        print(f"Coachテーブルで検索中: {email}")
        c = (await db.execute(select(Coach).where(Coach.email == email))).scalar_one_or_none()
        
        if c:
            print(f"Coachが見つかりました: {c.coach_id}")
            print(f"パスワード検証中...")
            if verify_password(form.password, c.password_hash):
                print(f"パスワード検証成功")
                expires = timedelta(minutes=settings.access_token_expire_minutes)
                token = create_access_token({"sub": str(c.coach_id), "role": "coach"}, expires)
                print(f"トークン生成成功: {token[:20]}...")
                return {"access_token": token, "token_type": "bearer", "role": "coach"}
            else:
                print(f"パスワード検証失敗")
        else:
            print(f"Coachが見つかりませんでした: {email}")

        print(f"認証失敗: メールアドレスまたはパスワードが正しくありません")
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
        
    except HTTPException:
        # HTTPExceptionは再送出
        raise
    except Exception as e:
        print(f"ログイン処理で予期しないエラーが発生: {str(e)}")
        print(f"エラータイプ: {type(e).__name__}")
        import traceback
        print(f"スタックトレース: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"ログイン処理でエラーが発生しました: {str(e)}")


# ---------------------------
# Me
# ---------------------------
@router.get("/me")
async def me(sub: str = Depends(get_current_user_strict), db: AsyncSession = Depends(get_database)):
    # sub は JWT の "sub"（= user_id or coach_id）
    u = (await db.execute(select(User).where(User.user_id == sub))).scalar_one_or_none()
    if u:
        return {"role": "user", "profile": UserMini.model_validate(u)}
    c = (await db.execute(select(Coach).where(Coach.coach_id == sub))).scalar_one_or_none()
    if c:
        return {"role": "coach", "profile": CoachOut.model_validate(c)}
    raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
