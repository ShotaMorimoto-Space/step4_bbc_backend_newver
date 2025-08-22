from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
import os
import urllib.parse

# .envファイルから環境変数を読み込む
load_dotenv()

#.envファイルからデータベース接続情報を取得(専用URLを最優先で採用（同期用）
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")
if DATABASE_URL_SYNC:
    # 念のため、非同期ドライバ指定が混ざっていても同期pymysqlに置換
    DATABASE_URL = (
        DATABASE_URL_SYNC
        .replace("mysql+aiomysql://", "mysql+pymysql://")
        .replace("mysql+asyncmy://", "mysql+pymysql://")
    )
else:

    # .envファイルからデータベース接続情報を取得
    DATABASE_HOST= os.getenv("DATABASE_HOST")
    DATABASE_PORT= os.getenv("DATABASE_PORT", "3306")
    DATABASE_NAME= os.getenv("DATABASE_NAME")
    DATABASE_USERNAME= os.getenv("DATABASE_USERNAME")
    DATABASE_PASSWORD= os.getenv("DATABASE_PASSWORD")

    # .pemファイル名を指定
    # ssl_cert = "DigiCertGlobalRootCA.crt (1).pem"
    ssl_cert = os.getenv("DATABASE_SSL_CA", "DigiCertGlobalRootCA.crt (1).pem")

    # SSL接続用のパラメータをURLに追加
    query = urllib.parse.urlencode({ "ssl_ca": ssl_cert })

    # MySQL接続URLを構築
    DATABASE_URL = f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?{query}"

# SQLAlchemyのエンジンとセッションを作成
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデル定義で継承するベースクラス
Base = declarative_base()

#DBのテスト用
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
