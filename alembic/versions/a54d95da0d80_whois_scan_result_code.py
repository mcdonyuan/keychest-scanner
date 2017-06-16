"""whois scan result code

Revision ID: a54d95da0d80
Revises: 2b0638d30d3e
Create Date: 2017-06-16 20:36:45.613583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a54d95da0d80'
down_revision = '2b0638d30d3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scan_jobs', sa.Column('crtsh_check_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_scan_jobs_crtsh_check_id'), 'scan_jobs', ['crtsh_check_id'], unique=False)
    op.create_foreign_key(None, 'scan_jobs', 'crtsh_query', ['crtsh_check_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'scan_jobs', type_='foreignkey')
    op.drop_index(op.f('ix_scan_jobs_crtsh_check_id'), table_name='scan_jobs')
    op.drop_column('scan_jobs', 'crtsh_check_id')
    # ### end Alembic commands ###
