-- データベースの制約を確認するSQLスクリプト
-- このスクリプトを実行して、section_groupsテーブルの制約を確認してください

-- 1. section_groupsテーブルの制約を確認
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

-- 2. 外部キー制約の詳細を確認
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME,
    UPDATE_RULE,
    DELETE_RULE
FROM 
    INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
JOIN 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu 
    ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
WHERE 
    kcu.TABLE_NAME = 'section_groups' 
    AND kcu.CONSTRAINT_SCHEMA = 'new_bbc_db';

-- 3. section_groupsテーブルの構造を確認
DESCRIBE section_groups;

-- 4. 外部キー制約を削除するSQL（必要に応じて実行）
-- ALTER TABLE section_groups DROP FOREIGN KEY section_groups_ibfk_2;
