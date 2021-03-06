"""045 management entries changes

Revision ID: 9735dbbb86c7
Revises: 47d998983ce2
Create Date: 2017-11-20 09:29:33.052081+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9735dbbb86c7'
down_revision = '47d998983ce2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('managed_hosts', sa.Column('ssh_key_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_managed_hosts_ssh_key_id'), 'managed_hosts', ['ssh_key_id'], unique=False)
    op.create_unique_constraint('uk_managed_hosts_host_uk', 'managed_hosts', ['host_addr', 'ssh_port', 'user_id', 'agent_id'])
    op.create_foreign_key('managed_hosts_ssh_keys_id', 'managed_hosts', 'ssh_keys', ['ssh_key_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('managed_hosts_ssh_keys_id', 'managed_hosts', type_='foreignkey')
    op.drop_constraint('uk_managed_hosts_host_uk', 'managed_hosts', type_='unique')
    op.drop_index(op.f('ix_managed_hosts_ssh_key_id'), table_name='managed_hosts')
    op.drop_column('managed_hosts', 'ssh_key_id')
    # ### end Alembic commands ###
