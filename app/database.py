from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator  # ← typing からインポートするのが正解
from app.core.config import settings

# --- MySQL 接続 URL の構築 ---
DATABASE_URL = (
    f"mysql+pymysql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_host}:{settings.database_port}/{settings.database_name}"
)

# --- エンジン作成 ---
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True if settings.env == "development" else False,  # ← ログ出力はENV依存にしてもよい
)

# --- セッション作成 ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 依存関係として使うDBセッション ---
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
