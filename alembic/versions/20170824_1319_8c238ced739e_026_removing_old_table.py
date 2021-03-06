"""026 removing old table

Revision ID: 8c238ced739e
Revises: 61f63a181d53
Create Date: 2017-08-24 13:19:31.115745+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8c238ced739e'
down_revision = '61f63a181d53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('last_record_cache')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('last_record_cache',
    sa.Column('id', mysql.BIGINT(display_width=20), nullable=False),
    sa.Column('record_key', mysql.VARCHAR(length=191), nullable=False),
    sa.Column('record_at', mysql.DATETIME(), nullable=True),
    sa.Column('record_id', mysql.BIGINT(display_width=20), autoincrement=False, nullable=True),
    sa.Column('record_aux', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    # ### end Alembic commands ###
