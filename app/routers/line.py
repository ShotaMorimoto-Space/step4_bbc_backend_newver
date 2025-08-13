# app/routers/line.py
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import uuid
from datetime import timedelta
from typing import Any, Dict, Optional

import aiohttp
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import get_db, User
from app.core.config import settings
from app.core.jwt import create_access_token
from app.core.security import get_password_hash
from app.utils.logger import logger
from app.services.storage import storage_service  # 画像保存で使用（動画はTODO）

router = APIRouter()

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
USE_DUMMY = not (LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN)


# ---------------------------
# ユーティリティ
# ---------------------------
async def ensure_guest_user(db: AsyncSession, line_user_id: str) -> User:
    """line_user_id で users を検索。なければ guest を自動作成して返す。"""
    existing = (await db.execute(
        select(User).where(User.line_user_id == line_user_id)
    )).scalar_one_or_none()

    if existing:
        return existing

    # ゲスト作成（emailはユニーク用のダミー、パスワードはランダムのハッシュ）
    random_pw = get_password_hash(str(uuid.uuid4()))
    guest = User(
        username=f"LINE_Guest_{line_user_id[-6:]}",
        email=f"line_{line_user_id}@example.local",
        usertype="guest",
        password_hash=random_pw,
        line_user_id=line_user_id,
        bio="Created via LINE webhook",
    )
    db.add(guest)
    await db.commit()
    await db.refresh(guest)
    return guest


async def verify_line_signature(body_bytes: bytes, signature_b64: str) -> bool:
    """X-Line-Signature 検証（本番用）。"""
    if USE_DUMMY:
        return True
    mac = hmac.new(LINE_CHANNEL_SECRET.encode("utf-8"), body_bytes, hashlib.sha256).digest()
    expected = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(expected, signature_b64 or "")


async def line_get_message_content(message_id: str) -> bytes:
    """メッセージバイナリを取得（画像/動画/音声）。"""
    if USE_DUMMY:
        # ダミー用: 空のバイト列
        return b"dummy"
    url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise HTTPException(500, f"LINE content fetch failed: {resp.status} {text}")
            return await resp.read()


async def line_reply(reply_token: str, texts: list[str]) -> None:
    """返信テキストを送信。"""
    if USE_DUMMY:
        logger.info(f"[DUMMY] reply -> {texts}")
        return
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": t[:1000]} for t in texts],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.warning(f"LINE reply error: {resp.status} {text}")


# ---------------------------
# 1) LINE Webhook（画像/動画受け取り）
# ---------------------------
@router.post("/webhook")
async def webhook(
    request: Request,
    x_line_signature: Optional[str] = Header(None, alias="X-Line-Signature"),
    db: AsyncSession = Depends(get_db),
):
    body_bytes = await request.body()

    # 署名検証
    if not await verify_line_signature(body_bytes, x_line_signature or ""):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload: Dict[str, Any] = await request.json()
    events = payload.get("events", [])
    logger.info(f"LINE events: {events}")

    for ev in events:
        etype = ev.get("type")
        source = ev.get("source", {})
        line_user_id = source.get("userId")
        reply_token = ev.get("replyToken")

        # ゲスト自動作成（なければ）
        if line_user_id:
            user = await ensure_guest_user(db, line_user_id)
            logger.info(f"guest ensured: user_id={user.user_id}")

        if etype == "message":
            msg = ev.get("message", {})
            mtype = msg.get("type")
            message_id = msg.get("id")

            # 画像
            if mtype == "image":
                try:
                    blob = await line_get_message_content(message_id)
                    # 画像保存（Azure Blob）
                    # ファイル名は一意っぽく
                    filename = f"line_img_{message_id}.jpg"
                    # storage_service は画像アップロードAPIがある想定
                    url = await storage_service.upload_image(io_bytes=blob, filename=filename)  # upload_imageがBytes/IO両対応ならOK
                    await line_reply(reply_token, ["画像を受け取りました。保存しました。", url if url else ""])
                except Exception as e:
                    logger.exception(e)
                    await line_reply(reply_token, ["画像の保存に失敗しました。"])

            # 動画
            elif mtype == "video":
                try:
                    blob = await line_get_message_content(message_id)
                    # TODO: 動画の保存。storage_service に汎用アップロードが無ければ実装が必要。
                    # いったん保存スキップして受領だけ返信。
                    await line_reply(reply_token, ["動画を受け取りました。（保存は今はスキップ）"])
                except Exception as e:
                    logger.exception(e)
                    await line_reply(reply_token, ["動画の取得に失敗しました。"])

            # 音声
            elif mtype == "audio":
                try:
                    blob = await line_get_message_content(message_id)
                    # TODO: audio 保存APIがあれば使う。なければスキップ。
                    await line_reply(reply_token, ["音声を受け取りました。（保存は今はスキップ）"])
                except Exception as e:
                    logger.exception(e)
                    await line_reply(reply_token, ["音声の取得に失敗しました。"])

            # テキスト
            elif mtype == "text":
                text = msg.get("text", "")
                # 簡単なハンドリング例
                if text.strip().lower() == "help":
                    await line_reply(reply_token, [
                        "画像・動画・音声を送ると受け取ります。",
                        "アプリ連携は /api/v1/line/login で行えます。",
                    ])
                else:
                    await line_reply(reply_token, [f"受け取りました: {text}"])

            else:
                await line_reply(reply_token, ["未対応のメッセージタイプです。"])

        else:
            # follow / unfollow / postback などはここで個別対応可能
            if reply_token:
                await line_reply(reply_token, ["イベントを受け取りました。"])

    return {"success": True}


# ---------------------------
# 2) LINE Login（IDトークン or 開発用line_user_id）→ JWT発行
# ---------------------------
class LineLoginRequest(BaseModel):
    id_token: Optional[str] = None   # 本番はこれを検証
    line_user_id: Optional[str] = None  # 開発用ショートカット


@router.post("/login")
async def line_login(payload: LineLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    - 本番：id_token を検証 → sub(=line_user_id) 抽出 → ゲスト確保/昇格 → JWT発行
    - 開発：line_user_id を直接受けてゲスト確保 → JWT発行
    """
    # 開発ショートカット
    if payload.line_user_id:
        user = await ensure_guest_user(db, payload.line_user_id)
    else:
        # 本番は id_token 検証が必要（ここではダミー対応）
        if USE_DUMMY or not payload.id_token:
            raise HTTPException(400, "id_token または line_user_id が必要です（開発中は line_user_id 推奨）")

        # 例: LINEの検証エンドポイントに対して検証（ここでは未実装）
        # 検証OK → line_user_id = sub
        # line_user_id = ...
        raise HTTPException(501, "id_token 検証は未実装です（本番時に実装してください）")

    # JWT 発行
    access_token = create_access_token(
        data={"sub": str(user.user_id), "role": "user"},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "user",
        "line_user_id": user.line_user_id,
        "user_id": str(user.user_id),
    }


# ---------------------------
# 3) 開発用: ダミー送信（動作確認）
# ---------------------------
class DevEchoRequest(BaseModel):
    text: str


@router.post("/dev/echo")
async def dev_echo(payload: DevEchoRequest):
    return {"echo": payload.text}
