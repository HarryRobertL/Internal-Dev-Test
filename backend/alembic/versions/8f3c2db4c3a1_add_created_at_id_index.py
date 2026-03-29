"""add customers list index

Revision ID: 8f3c2db4c3a1
Revises: 67c84f970ba5
Create Date: 2026-03-29 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8f3c2db4c3a1'
down_revision: Union[str, Sequence[str], None] = '67c84f970ba5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        'ix_customers_created_at_id',
        'customers',
        ['created_at', 'id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_customers_created_at_id', table_name='customers')
