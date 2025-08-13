# app/main.py
from __future__ import annotations

import os
import io
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

from app.models import create_tables
from app.core.config import settings
from app.services.storage import storage_service

# Routers
from app.routers import auth, user, video, coach, upload, transcription, line


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown（必要なら後処理）


app = FastAPI(
    title="Golf Swing Coaching API",
    description="API for managing golf swing video coaching feedback",
    version="1.0.0",
    lifespan=lifespan,
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # 例: FRONTEND_ORIGINS=http://localhost:3000,https://example.com
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Static ----
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ---- Routers ----
app.include_router(auth.router,           prefix="/api/v1/auth",  tags=["auth"])
app.include_router(user.router,           prefix="/api/v1",       tags=["users"])
app.include_router(video.router,          prefix="/api/v1",       tags=["videos"])
app.include_router(coach.router,          prefix="/api/v1",       tags=["coach"])
app.include_router(upload.router,         prefix="/api/v1",       tags=["upload"])
app.include_router(transcription.router,  prefix="/api/v1",       tags=["transcription"])
app.include_router(line.router, prefix="/api/v1/line", tags=["line"])

# ---- Health / Root ----
@app.get("/")
async def root():
    return {"message": "Golf Swing Coaching API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ---- SAS URL 生成（動作確認済みバージョン）----
@app.get("/media-url")
def get_media_url(blob_url: str):
    """
    Azure Blob Storage のファイルから SAS URL を生成
    """
    try:
        # blob_url から blob のパス（container 配下）を抽出
        if blob_url.startswith("https://"):
            # https://{account}.blob.core.windows.net/{container}/{path...}
            parts = blob_url.split("/")
            filename = "/".join(parts[4:])  # container 以降
        else:
            filename = blob_url

        # Azure 設定
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER", "bbc-test")
        if not connection_string:
            raise HTTPException(status_code=500, detail="Azure接続設定が見つかりません")

        # Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        account_key = blob_service_client.credential.account_key
        account_name = blob_service_client.account_name

        # SAS トークン（15分）
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=filename,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=15),
        )
        sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{filename}?{sas_token}"
        return {"url": sas_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Azure Blob のプロキシ（SAS を内部発行して取得）----
@app.get("/proxy-file/{file_path:path}")
async def proxy_file(file_path: str):
    """
    Azure Blob Storage ファイルのプロキシエンドポイント
    """
    try:
        from fastapi.responses import Response
        import urllib.parse
        import aiohttp

        decoded_file_path = urllib.parse.unquote(file_path)

        # SAS URL を取得
        media_response = get_media_url(decoded_file_path)
        sas_url = media_response["url"]

        # 取得してプロキシ
        async with aiohttp.ClientSession() as session:
            async with session.get(sas_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="ファイルの取得に失敗しました")
                content = await response.read()
                content_type = response.headers.get("content-type", "application/octet-stream")
                return Response(
                    content=content,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0",
                    },
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルプロキシエラー: {str(e)}")


# ---- 画像アップロード（セクション切り出し画像）----
@app.post("/upload-section-image")
async def upload_section_image(image_file: UploadFile = File(...)):
    """
    セクション切り出し画像を Azure Blob Storage にアップロード
    """
    try:
        if not image_file.content_type or not image_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="画像ファイルのみアップロード可能です")

        file_content = await image_file.read()
        file_stream = io.BytesIO(file_content)

        image_url = await storage_service.upload_image(file_stream, image_file.filename or "section_image.jpg")
        return {"success": True, "image_url": image_url, "message": "画像のアップロードが完了しました"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像アップロードに失敗しました: {str(e)}")


# ---- 画像アップロード（マークアップ画像：Base64入力）----
@app.post("/upload-markup-image")
async def upload_markup_image(
    image_data: str = Form(...),
    filename: str = Form(...),
    original_url: str = Form(...),
):
    """
    マークアップ画像（Base64）を Azure Blob Storage にアップロード
    """
    try:
        import base64

        # Base64 抽出
        if image_data.startswith("data:image/"):
            _, base64_data = image_data.split(",", 1)
        else:
            base64_data = image_data

        try:
            file_content = base64.b64decode(base64_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Base64デコードに失敗しました: {str(e)}")

        file_stream = io.BytesIO(file_content)
        image_url = await storage_service.upload_image(file_stream, filename)

        return {"success": True, "image_url": image_url, "message": "マークアップ画像のアップロードが完了しました", "original_url": original_url}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"マークアップ画像アップロードに失敗しました: {str(e)}")
