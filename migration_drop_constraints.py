"""Drop foreign key constraints from section_groups table

Revision ID: drop_section_groups_constraints
Revises: 
Create Date: 2025-08-27 17:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'drop_section_groups_constraints'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Drop foreign key constraints from section_groups table"""
    
    # 外部キー制約を削除
    try:
        op.drop_constraint('section_groups_ibfk_2', 'section_groups', type_='foreignkey')
        print("Successfully dropped foreign key constraint: section_groups_ibfk_2")
    except Exception as e:
        print(f"Warning: Could not drop constraint section_groups_ibfk_2: {e}")
    
    # 他の可能性のある外部キー制約も削除
    try:
        op.drop_constraint('section_groups_ibfk_1', 'section_groups', type_='foreignkey')
        print("Successfully dropped foreign key constraint: section_groups_ibfk_1")
    except Exception as e:
        print(f"Warning: Could not drop constraint section_groups_ibfk_1: {e}")
    
    # session_idカラムの型をVARCHAR(255)に変更
    try:
        op.alter_column('section_groups', 'session_id',
                       existing_type=sa.String(36),
                       type_=sa.String(255),
                       existing_nullable=True)
        print("Successfully changed session_id column type to VARCHAR(255)")
    except Exception as e:
        print(f"Warning: Could not change session_id column type: {e}")

def downgrade():
    """Recreate foreign key constraints (if needed)"""
    
    # 注意: このダウングレードは実行しないでください
    # 外部キー制約を再作成すると、同じ問題が発生します
    print("Warning: Downgrade not implemented to avoid recreating problematic constraints")
    pass
