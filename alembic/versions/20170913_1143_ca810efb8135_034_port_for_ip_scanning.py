"""034 port for ip scanning

Revision ID: ca810efb8135
Revises: 42dba2fe7097
Create Date: 2017-09-13 11:43:56.038244+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca810efb8135'
down_revision = '42dba2fe7097'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ip_scan_record', sa.Column('service_port', sa.Integer(), nullable=False, server_default='443'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ip_scan_record', 'service_port')
    # ### end Alembic commands ###
