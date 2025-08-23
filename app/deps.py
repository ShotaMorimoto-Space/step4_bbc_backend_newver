# app/deps.py
from __future__ import annotations

import os
from typing import Optional, Generator  # AsyncGeneratorからGeneratorに変更

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session  # AsyncSessionからSessionに変更

from app.database import get_db  # 正しいモジュールからインポート
from app.core.jwt import decode_access_token  # JWTデコード（app/core/jwt.py）

load_dotenv()

# 本番ルートに合わせる（/api/v1 を使わないなら "/auth/token" に変更）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_database() -> Generator[Session, None, None]:
    """Sync DB session dependency"""
    # 同期的なget_dbを使用
    for session in get_db():
        yield session

def get_default_user_id() -> str:
    """Dev用の固定ユーザーID（.env: DEFAULT_USER_ID が優先）"""
    return os.getenv("DEFAULT_USER_ID", "550e8400-e29b-41d4-a716-446655440000")

def get_default_coach_id() -> str:
    """Dev用の固定コーチID（.env: DEFAULT_COACH_ID が優先）"""
    return os.getenv("DEFAULT_COACH_ID", "6ba7b810-9dad-11d1-80b4-00c04fd430c8")

# ---------- 認証切替ポイント ----------
def get_current_user_or_dummy(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_database),  # 将来のユーザー検証用に保持
) -> str:
    """
    開発中：トークンが無ければデフォルトIDを返す。
    トークンがあれば検証して sub（= user_id）を返す。
    """
    if not token:
        return get_default_user_id()
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("no sub in token")
        # 必要ならここでDBからユーザー確認（例）
        # user = await user_crud.get(db, sub)
        # if not user or not user.is_active:
        #     raise ValueError("inactive/unknown user")
        return sub
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

def get_current_user_strict(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_database),
) -> str:
    """
    本番で“ログイン必須”にする場合はこちらをDependsに。
    トークン必須・不正なら401。
    """
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    # 必要ならDB検証
    # user = await user_crud.get(db, sub)
    # if not user or not user.is_active:
    #     raise HTTPException(status_code=401, detail="User not active")
    return sub
# ---------- ここまで ----------
