# app/services/transcription.py
from __future__ import annotations

import os
import tempfile
from typing import BinaryIO, Optional, TYPE_CHECKING

from dotenv import load_dotenv

# 型チェック専用のインポート（実行時には読み込まれない）
if TYPE_CHECKING:
    from openai import OpenAI as OpenAIClientType

# 実行時の安全インポート
try:
    from openai import OpenAI as _OpenAIRuntime, OpenAIError  # openai==1.x
except Exception:
    _OpenAIRuntime = None  # 実行時に OpenAI が無くても落とさない
    class OpenAIError(Exception): ...
load_dotenv()


class TranscriptionService:
    """Service for audio transcription using OpenAI Whisper"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        # クライアント型（型チェック時のみ有効）。実行時は None でOK
        self.client: Optional["OpenAIClientType"] = None
        self.use_dummy = not api_key or _OpenAIRuntime is None

        if self.use_dummy:
            print("OpenAI API key not configured, using dummy transcription")
        else:
            try:
                self.client = _OpenAIRuntime(api_key=api_key)
            except Exception as e:
                print(f"OpenAI init failed: {e}; falling back to dummy transcription")
                self.use_dummy = True
                self.client = None

    async def transcribe_audio(self, audio_file: BinaryIO, language: str = "ja") -> str:
        """
        Transcribe audio file using OpenAI Whisper
        """
        if self.use_dummy:
            return "こちらはダミーの文字起こし結果です。スイングの改善点について説明しています。アドレスの姿勢を意識して、体重移動をスムーズに行いましょう。"

        import os.path
        suffix = os.path.splitext(getattr(audio_file, "name", "") or "")[1] or ".wav"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            audio_file.seek(0)
            tmp.write(audio_file.read())
            tmp_path = tmp.name

        try:
            assert self.client is not None  # 型安心のため
            with open(tmp_path, "rb") as f:
                result = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language,
                    prompt="これはゴルフのコーチングセッションの音声です。ゴルフ用語や技術的な指導内容が含まれています。",
                    response_format="text",
                )
            return result if isinstance(result, str) else getattr(result, "text", "")
        except OpenAIError as e:
            raise Exception(f"音声の文字起こしに失敗しました: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    async def transcribe_audio_with_timestamps(self, audio_file: BinaryIO, language: str = "ja") -> dict:
        """
        Transcribe audio with timestamp information
        """
        if self.use_dummy:
            return {
                "text": "（ダミー）タイムスタンプ付き文字起こしは無効です。",
                "language": "ja",
                "duration": 0,
                "segments": [],
            }

        import os.path
        suffix = os.path.splitext(getattr(audio_file, "name", "") or "")[1] or ".wav"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            audio_file.seek(0)
            tmp.write(audio_file.read())
            tmp_path = tmp.name

        try:
            assert self.client is not None
            with open(tmp_path, "rb") as f:
                result = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language,
                    prompt="これはゴルフのコーチングセッションの音声です。ゴルフ用語や技術的な指導内容が含まれています。",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                )

            text = getattr(result, "text", None) or result.get("text", "")
            language = getattr(result, "language", None) or result.get("language", "ja")
            duration = getattr(result, "duration", None) or result.get("duration", 0)
            segments = getattr(result, "segments", None) or result.get("segments", [])

            normalized_segments = []
            for s in segments:
                start = getattr(s, "start", None) if hasattr(s, "start") else s.get("start")
                end = getattr(s, "end", None) if hasattr(s, "end") else s.get("end")
                txt = getattr(s, "text", None) if hasattr(s, "text") else s.get("text")
                normalized_segments.append({"start": start, "end": end, "text": txt})

            return {"text": text, "language": language, "duration": duration, "segments": normalized_segments}
        except OpenAIError as e:
            raise Exception(f"タイムスタンプ付き文字起こしに失敗しました: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    async def validate_audio_format(self, audio_file: BinaryIO) -> bool:
        """
        Validate if audio file format is supported by Whisper
        """
        if self.use_dummy:
            return True

        import os.path
        supported = {".m4a", ".mp3", ".mp4", ".mpeg", ".mpga", ".wav", ".webm"}
        filename = getattr(audio_file, "name", "")
        return os.path.splitext(filename.lower())[1] in supported if filename else True


# Global instance
transcription_service = TranscriptionService()
