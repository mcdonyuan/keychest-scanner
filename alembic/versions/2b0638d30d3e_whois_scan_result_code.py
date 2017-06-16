"""whois scan result code

Revision ID: 2b0638d30d3e
Revises: 68793266cf2c
Create Date: 2017-06-16 20:17:52.113121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b0638d30d3e'
down_revision = '68793266cf2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('whois_result', sa.Column('result', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('whois_result', 'result')
    # ### end Alembic commands ###
