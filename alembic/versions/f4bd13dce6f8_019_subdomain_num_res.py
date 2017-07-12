"""019 subdomain num res

Revision ID: f4bd13dce6f8
Revises: 7808de10af98
Create Date: 2017-07-12 17:24:30.084624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4bd13dce6f8'
down_revision = '7808de10af98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subdomain_results', sa.Column('result_size', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subdomain_results', 'result_size')
    # ### end Alembic commands ###