"""050 cert price list

Revision ID: 1d973942057b
Revises: a2d90960dfdd
Create Date: 2017-11-29 14:13:45.021827+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d973942057b'
down_revision = 'a2d90960dfdd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('certificate_price_list',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('issuer_org', sa.String(length=255), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('price_personal', sa.Float(), nullable=True),
    sa.Column('price_ov', sa.Float(), nullable=True),
    sa.Column('price_ev', sa.Float(), nullable=True),
    sa.Column('price_wildcard', sa.Float(), nullable=True),
    sa.Column('price_ev_wildcard', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('certificate_price_list')
    # ### end Alembic commands ###
