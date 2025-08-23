# app/routers/transcription.py
from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, TYPE_CHECKING
import os
import tempfile
import io
from datetime import datetime
from dotenv import load_dotenv

from app.utils.logger import logger
from app.services.storage import storage_service

# 型チェック専用の型（実行時には評価されない）
if TYPE_CHECKING:
    from openai import OpenAI as OpenAIClientType

# 実行時の安全インポート（失敗しても落とさない）
try:
    from openai import OpenAI as _OpenAIRuntime, OpenAIError
except Exception:
    _OpenAIRuntime = None
    class OpenAIError(Exception): ...
load_dotenv()


def generate_audio_filename(type: str, video_filename: Optional[str] = None, phase_code: Optional[str] = None) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if type == "phase_advice" and phase_code:
        return f"{timestamp}_{phase_code}_audio.wav"
    elif type == "advice":
        return f"{timestamp}_advice_audio.wav"
    elif type == "practice":
        return f"{timestamp}_practice_audio.wav"
    else:
        return f"{timestamp}_general_audio.wav"


router = APIRouter(tags=["transcription"])


def get_openai_client() -> Optional["OpenAIClientType"]:
    """必要なときだけ OpenAI クライアントを初期化（キー未設定なら None）"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or _OpenAIRuntime is None:
        return None
    try:
        return _OpenAIRuntime(api_key=api_key)  # 実行時はこちらを使う
    except Exception as e:
        logger.warning(f"OpenAI init failed: {e}")
        return None


@router.post("/transcribe-audio")
def transcribe_audio(
    audio: UploadFile = File(...),
    type: Optional[str] = Form("general"),
    video_filename: Optional[str] = Form(None),
    phase_code: Optional[str] = Form(None),
):
    """音声を Whisper で文字起こし（キー未設定ならダミー返却／アプリは落とさない）"""
    try:
        logger.info(f"音声文字起こし開始: ファイル名={audio.filename}, タイプ={type}")

        if not audio.content_type or not audio.content_type.startswith("audio/"):
            logger.error(f"無効なファイル形式: {audio.content_type}")
            raise HTTPException(status_code=400, detail="音声ファイルをアップロードしてください")

        # 一時ファイルへ保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            audio_content = await audio.read()
            temp_file.write(audio_content)
            temp_file.flush()

        try:
            file_size = os.path.getsize(temp_file_path)
            logger.info(f"一時ファイル作成: {temp_file_path} / {file_size} bytes")
            if file_size < 1000:
                logger.warning(f"音声ファイルサイズが小さすぎます: {file_size} bytes")
                return {
                    "success": False,
                    "transcription": "音声データが検出されませんでした。録音時間が短すぎるか、マイクの音量が低い可能性があります。",
                    "type": type,
                    "audio_url": None,
                    "audio_filename": None,
                    "audio_duration": None,
                }

            client = get_openai_client()
            if client is None:
                logger.warning("OpenAI APIキー未設定/初期化失敗。ダミーの文字起こし結果を返します。")
                return {
                    "success": True,
                    "transcription": "OpenAI APIキーが設定されていないため、ダミーの文字起こし結果です。実際の音声を文字起こしするには、環境変数OPENAI_API_KEYを設定してください。",
                    "type": type,
                    "audio_url": None,
                    "audio_filename": None,
                    "audio_duration": None,
                }

            # Whisper で文字起こし
            logger.info("Whisper APIで文字起こし中...")
            with open(temp_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja",
                    prompt="これはゴルフのスイング指導に関する音声です。専門用語や技術的な内容が含まれます。",
                )
            transcription_text = getattr(transcript, "text", "") or ""

            # 怪しい結果の簡易フィルタ
            suspicious_phrases = [
                "ご視聴ありがとうございました",
                "ありがとうございました",
                "Thanks for watching",
                "Thank you for watching",
            ]
            if any(p in transcription_text for p in suspicious_phrases):
                logger.warning(f"疑わしい文字起こし結果: {transcription_text}")
                transcription_text = "録音された音声が検出されませんでした。マイクの設定を確認して、もう一度録音してください。"

            # Blob 保存（メソッド差異にフォールバック）
            audio_url = None
            audio_filename = generate_audio_filename(type or "general", video_filename, phase_code)
            try:
                audio_stream = io.BytesIO(audio_content)
                if hasattr(storage_service, "upload_audio_with_exact_name"):
                    audio_url = await storage_service.upload_audio_with_exact_name(audio_stream, audio_filename)
                elif hasattr(storage_service, "storage"):
                    audio_url = await storage_service.storage.upload_file_with_exact_name(
                        audio_stream, audio_filename, content_type="audio/wav"
                    )
                else:
                    audio_url = await storage_service.storage.upload_file(
                        audio_stream, audio_filename, content_type="audio/wav"
                    )
                logger.info(f"音声ファイル保存完了: {audio_url}")
            except Exception as e:
                logger.warning(f"音声ファイル保存失敗: {e}（文字起こしは成功）")

            return {
                "success": True,
                "transcription": transcription_text,
                "type": type,
                "audio_url": audio_url,
                "audio_filename": audio_filename,
                "audio_duration": None,
            }

        finally:
            try:
                os.unlink(temp_file_path)
                logger.info(f"一時ファイル削除: {temp_file_path}")
            except Exception as e:
                logger.warning(f"一時ファイル削除失敗: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"音声文字起こしエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"音声の文字起こしに失敗しました: {str(e)}")
