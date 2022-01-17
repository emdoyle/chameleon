"""Add session ordering to SetUpPhase

Revision ID: 27425e1cbb40
Revises: 94ea035bca37
Create Date: 2020-03-28 16:41:53.298917

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "27425e1cbb40"
down_revision = "94ea035bca37"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "setup_phases",
        sa.Column("session_ordering", postgresql.ARRAY(sa.Integer()), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("setup_phases", "session_ordering")
    # ### end Alembic commands ###
