#!/usr/bin/env python3
"""
MySQL テーブル作成スクリプト - 初期設計に基づく
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from app.models import Base

load_dotenv()

def create_mysql_tables():
    """MySQL にテーブルを作成"""
    
    # MySQL用のDATABASE_URLを設定
    mysql_url = os.getenv("MYSQL_DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/golf_coaching")
    
    print(f"🔗 MySQL接続: {mysql_url.replace('password', '****')}")
    
    try:
        # MySQL エンジンを作成
        engine = create_engine(mysql_url, echo=True)
        
        print("📋 テーブル作成開始...")
        
        # テーブル作成
        with engine.begin() as conn:
            Base.metadata.create_all(conn)
        
        print("✅ テーブル作成完了!")
        
        # 作成されたテーブルを確認
        with engine.begin() as conn:
            result = conn.execute("SHOW TABLES")
            tables = result.fetchall()
            print(f"📊 作成されたテーブル: {[table[0] for table in tables]}")
            
        engine.dispose()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print("💡 MySQL サービスが起動していることを確認してください")
        print("💡 データベース 'golf_coaching' が存在することを確認してください")
        print("\n📝 データベース作成コマンド:")
        print("mysql -u root -p -e \"CREATE DATABASE IF NOT EXISTS golf_coaching;\"")
        sys.exit(1)

if __name__ == "__main__":
    create_mysql_tables()