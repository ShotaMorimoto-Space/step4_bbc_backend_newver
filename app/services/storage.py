# app/services/storage.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, List, Dict, Any
import os
import shutil
from pathlib import Path
import uuid
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, unquote
import json

from concurrent.futures import ThreadPoolExecutor
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    ContainerClient,
    ContentSettings,
)

from dotenv import load_dotenv

load_dotenv()


# ==============================
# Storage Interfaces
# ==============================
class StorageInterface(ABC):
    """Abstract interface for storage operations"""

    @abstractmethod
    def upload_file(self, file: BinaryIO, filename: str, content_type: Optional[str] = None) -> str:
        """Upload a file and return the URL"""
        raise NotImplementedError

    @abstractmethod
    def upload_file_with_exact_name(self, file: BinaryIO, exact_filename: str, content_type: Optional[str] = None) -> str:
        """Upload a file with exact filename (no modifications) and return the URL"""
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, file_url_or_path: str) -> bool:
        """Delete a file by URL (or blob path)"""
        raise NotImplementedError

    @abstractmethod
    def get_file_url(self, filename_or_path: str) -> str:
        """Get the URL for a file"""
        raise NotImplementedError

    # 追加：マークアップ等のJSON保存/取得
    def save_json(self, blob_path: str, data: Dict[str, Any]) -> str:
        """Save dict as JSON and return its URL"""
        raise NotImplementedError

    def get_json(self, blob_path: str) -> Optional[Dict[str, Any]]:
        """Get JSON (dict) from storage"""
        raise NotImplementedError

    def list_files(self, prefix: str = "") -> List[str]:
        """List file paths under prefix"""
        raise NotImplementedError


# ==============================
# Local Storage Implementation
# ==============================
class LocalStorage(StorageInterface):
    """Local file storage implementation"""

    def __init__(self, storage_path: str = "./uploads"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.base_url = "/uploads"  # Next.js のリバースプロキシ想定

    def upload_file(self, file: BinaryIO, filename: str, content_type: Optional[str] = None) -> str:
        """Upload file to local storage"""
        file_extension = Path(filename).suffix
        jst = timezone(timedelta(hours=9))
        now = datetime.now(jst)
        timestamp = now.strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_U99999{file_extension}"

        file_path = self.storage_path / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)

        return f"{self.base_url}/{unique_filename}"

    def upload_file_with_exact_name(self, file: BinaryIO, exact_filename: str, content_type: Optional[str] = None) -> str:
        """Upload file to local storage with exact filename"""
        file_path = self.storage_path / exact_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)
        return f"{self.base_url}/{exact_filename}"

    def delete_file(self, file_url_or_path: str) -> bool:
        """Delete file from local storage"""
        try:
            # URL or path のどちらでもOKにする
            name = self._extract_local_name(file_url_or_path)
            file_path = self.storage_path / name
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_url(self, filename_or_path: str) -> str:
        """Get URL for local file"""
        # 先頭に '/' があればそのまま返す
        if filename_or_path.startswith("/"):
            return filename_or_path
        return f"{self.base_url}/{filename_or_path}"

    def save_json(self, blob_path: str, data: Dict[str, Any]) -> str:
        """Save dict as JSON file locally"""
        target = self.storage_path / blob_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return self.get_file_url(blob_path)

    def get_json(self, blob_path: str) -> Optional[Dict[str, Any]]:
        target = self.storage_path / blob_path
        if not target.exists():
            return None
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def list_files(self, prefix: str = "") -> List[str]:
        base = self.storage_path / prefix if prefix else self.storage_path
        if not base.exists():
            return []
        paths: List[str] = []
        for p in base.rglob("*"):
            if p.is_file():
                rel = p.relative_to(self.storage_path).as_posix()
                paths.append(rel)
        return paths

    def _extract_local_name(self, file_url_or_path: str) -> str:
        # "/uploads/xxx" → "xxx"
        p = file_url_or_path
        if p.startswith(self.base_url):
            p = p[len(self.base_url):]
        return p.lstrip("/")


# ==============================
# Azure Blob Storage Implementation
# ==============================
class AzureBlobStorage(StorageInterface):
    """Azure Blob Storage implementation"""

    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER", "bbc-test")

        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is required for Azure Blob Storage")

        self.blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client: ContainerClient = self.blob_service_client.get_container_client(self.container_name)
        self.account_name: str = self.blob_service_client.account_name
        self.executor = ThreadPoolExecutor(max_workers=4)

    # ---------- helpers ----------
    def _blob_client(self, blob_path: str) -> BlobClient:
        return self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_path)

    def _extract_blob_path_from_url(self, file_url_or_path: str) -> str:
        """
        URL (SAS付きでもOK) から blob のパス（コンテナ配下パス）を抽出。
        すでに "dir/file.ext" 形式が渡ってきた場合はそのまま返す。
        """
        if "://" not in file_url_or_path and not file_url_or_path.startswith("/"):
            # 既に blob path とみなす
            return file_url_or_path

        parsed = urlparse(file_url_or_path)
        # 例: /<container>/dir/file.jpg
        path = unquote(parsed.path).lstrip("/")
        if not path:
            return ""
        # コンテナ名を取り除く
        if path.startswith(f"{self.container_name}/"):
            return path[len(self.container_name) + 1 :]
        # まれにアカウント直下書式もあるが、通常は上記でOK
        # 念のため最後のセグメントにフォールバック（非推奨だが後方互換用）
        return path.split("/", 1)[-1]

    # ---------- core ops ----------
    def upload_file(self, file: BinaryIO, filename: str, content_type: Optional[str] = None) -> str:
        """Upload file to Azure Blob Storage with unique name"""
        file_extension = Path(filename).suffix
        jst = timezone(timedelta(hours=9))
        now = datetime.now(jst)
        timestamp = now.strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_U99999{file_extension}"

        blob_client = self._blob_client(unique_filename)

        blob_client.upload_blob(
            file,
            content_settings=ContentSettings(content_type=content_type) if content_type else None,
            overwrite=True,
        )
        return blob_client.url

    def upload_file_with_exact_name(self, file: BinaryIO, exact_filename: str, content_type: Optional[str] = None) -> str:
        """Upload file to Azure Blob Storage with exact filename"""
        blob_client = self._blob_client(exact_filename)

        blob_client.upload_blob(
            file,
            content_settings=ContentSettings(content_type=content_type) if content_type else None,
            overwrite=True,
        )
        return blob_client.url

    def delete_file(self, file_url_or_path: str) -> bool:
        """Delete blob by URL or blob-path"""
        try:
            blob_path = self._extract_blob_path_from_url(file_url_or_path)
            if not blob_path:
                return False
            blob_client = self._blob_client(blob_path)

            try:
                blob_client.delete_blob()
                return True
            except Exception:
                return False
        except Exception:
            return False

    def get_file_url(self, filename_or_path: str) -> str:
        """Get URL for Azure blob (no SAS)"""
        blob_client = self._blob_client(filename_or_path)
        return blob_client.url

    # ---------- JSON helpers ----------
    def save_json(self, blob_path: str, data: Dict[str, Any]) -> str:
        """
        Save dict as JSON blob (UTF-8).
        Returns public (non-SAS) blob URL.
        """
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        blob_client = self._blob_client(blob_path)

        blob_client.upload_blob(
            payload,
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json"),
        )
        return blob_client.url

    def get_json(self, blob_path: str) -> Optional[Dict[str, Any]]:
        blob_client = self._blob_client(blob_path)

        try:
            stream = blob_client.download_blob()
            raw = stream.readall()
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def list_files(self, prefix: str = "") -> List[str]:
        try:
            res = []
            for blob in self.container_client.list_blobs(name_starts_with=prefix):
                res.append(blob.name)
            return res
        except Exception:
            return []

    def __del__(self):
        """Cleanup executor on deletion"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)


# ==============================
# Storage Service Facade
# ==============================
class StorageService:
    """Storage service factory and thin facade"""

    def __init__(self):
        storage_type = os.getenv("STORAGE_TYPE", "local").lower()

        if storage_type == "azure_blob":
            self.storage: StorageInterface = AzureBlobStorage()
        else:
            # Default to local storage
            storage_path = os.getenv("LOCAL_STORAGE_PATH", "./uploads")
            self.storage = LocalStorage(storage_path)

    # ---- Common wrappers (existing API) ----
    def upload_video(self, file: BinaryIO, filename: str) -> str:
        return self.storage.upload_file(file, filename, "video/mp4")

    def upload_image(self, file: BinaryIO, filename: str) -> str:
        return self.storage.upload_file(file, filename, "image/jpeg")

    def upload_image_with_exact_name(self, file: BinaryIO, exact_filename: str) -> str:
        return self.storage.upload_file_with_exact_name(file, exact_filename, "image/jpeg")

    def delete_file(self, file_url_or_path: str) -> bool:
        return self.storage.delete_file(file_url_or_path)

    def get_file_url(self, filename_or_path: str) -> str:
        return self.storage.get_file_url(filename_or_path)

    # ---- New: JSON helpers for markups/metadata ----
    def save_json(self, blob_path: str, data: Dict[str, Any]) -> str:
        """
        Save dict as JSON (Azure or Local). Return URL/path.
        ex) blob_path = "markups/{video_id}.json"
        """
        return self.storage.save_json(blob_path, data)

    def get_json(self, blob_path: str) -> Optional[Dict[str, Any]]:
        return self.storage.get_json(blob_path)

    def list_files(self, prefix: str = "") -> List[str]:
        return self.storage.list_files(prefix)


# Global storage service instance
storage_service = StorageService()
