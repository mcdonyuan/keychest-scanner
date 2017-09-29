"""039 api tasks

Revision ID: a7771c831cdc
Revises: ca9f16b7ecb2
Create Date: 2017-09-29 09:40:14.342663+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a7771c831cdc'
down_revision = 'ca9f16b7ecb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('api_waiting',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('api_key_id', sa.BigInteger(), nullable=True),
    sa.Column('object_operation', sa.String(length=42), nullable=True),
    sa.Column('object_type', sa.String(length=42), nullable=True),
    sa.Column('object_key', sa.String(length=191), nullable=True),
    sa.Column('object_value', sa.Text(), nullable=True),
    sa.Column('certificate_id', sa.BigInteger(), nullable=True),
    sa.Column('computed_data', sa.Text(), nullable=True),
    sa.Column('ct_scanned_at', sa.DateTime(), nullable=True),
    sa.Column('ct_found_at', sa.DateTime(), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.Column('finished_at', sa.DateTime(), nullable=True),
    sa.Column('approval_status', sa.SmallInteger(), nullable=False, server_default='0'),
    sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], name='fk_api_waiting_api_key_id', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['certificate_id'], ['certificates.id'], name='fk_api_waiting_certificate_id', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_waiting_api_key_id'), 'api_waiting', ['api_key_id'], unique=False)
    op.create_index(op.f('ix_api_waiting_certificate_id'), 'api_waiting', ['certificate_id'], unique=False)
    op.create_index(op.f('ix_api_waiting_object_key'), 'api_waiting', ['object_key'], unique=False)
    op.create_index(op.f('ix_api_waiting_object_operation'), 'api_waiting', ['object_operation'], unique=False)
    op.create_index(op.f('ix_api_waiting_object_type'), 'api_waiting', ['object_type'], unique=False)
    op.alter_column('access_tokens', 'num_sent',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True,
               existing_server_default=sa.text(u"'0'"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('access_tokens', 'num_sent',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False,
               existing_server_default=sa.text(u"'0'"))
    op.drop_index(op.f('ix_api_waiting_object_type'), table_name='api_waiting')
    op.drop_index(op.f('ix_api_waiting_object_operation'), table_name='api_waiting')
    op.drop_index(op.f('ix_api_waiting_object_key'), table_name='api_waiting')
    op.drop_table('api_waiting')
    # ### end Alembic commands ###
