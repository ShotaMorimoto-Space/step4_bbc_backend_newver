-- profile_picture_urlカラムをTEXT型に変更
-- このスクリプトは、profile_picture_urlカラムの長さ制限を解決します

-- 既存のデータをバックアップ（オプション）
-- CREATE TABLE users_backup AS SELECT * FROM users;

-- カラムの型をTEXTに変更
ALTER TABLE users MODIFY COLUMN profile_picture_url TEXT;

-- 変更の確認
DESCRIBE users;
