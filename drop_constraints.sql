-- 外部キー制約を削除するSQLスクリプト
-- このスクリプトを実行して、section_groupsテーブルの外部キー制約を削除してください

-- 1. 外部キー制約を削除
ALTER TABLE section_groups DROP FOREIGN KEY section_groups_ibfk_2;

-- 2. session_idカラムの型を変更（必要に応じて）
-- ALTER TABLE section_groups MODIFY COLUMN session_id VARCHAR(255);

-- 3. 制約が削除されたか確認
SELECT 
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE 
    TABLE_NAME = 'section_groups' 
    AND CONSTRAINT_SCHEMA = 'new_bbc_db';
