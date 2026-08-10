"""Store the final model output as scam risk.

Revision ID: 20260810_02
Revises: 20260809_01
Create Date: 2026-08-10 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260810_02"
down_revision = "20260809_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("analyses", "confidence", new_column_name="scam_risk")
    # Old legitimate results stored classification confidence (1 - scam risk).
    # Convert them so every existing row has the new, unambiguous meaning.
    op.execute(
        sa.text(
            "UPDATE analyses "
            "SET scam_risk = 1 - scam_risk "
            "WHERE prediction = 'legitimate' AND scam_risk IS NOT NULL"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE analyses "
            "SET scam_risk = 1 - scam_risk "
            "WHERE prediction = 'legitimate' AND scam_risk IS NOT NULL"
        )
    )
    op.alter_column("analyses", "scam_risk", new_column_name="confidence")
