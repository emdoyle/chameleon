"""Add winner to Round model

Revision ID: 94ea035bca37
Revises: 
Create Date: 2020-03-28 16:16:01.430362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "94ea035bca37"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("rounds", sa.Column("winner", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("rounds", "winner")
    # ### end Alembic commands ###
