"""002 extended ct scans

Revision ID: 9a255012d5e3
Revises: 9a250012d5e3
Create Date: 2017-07-04 20:24:01.388040

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9a255012d5e3'
down_revision = '9a250012d5e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subdomain_scan_blacklist',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('rule', sa.String(length=255), nullable=False),
                    sa.Column('rule_type', sa.SmallInteger(), nullable=True),
                    sa.Column('detection_code', sa.SmallInteger(), nullable=True),
                    sa.Column('detection_value', sa.Integer(), nullable=True),
                    sa.Column('detection_first_at', sa.DateTime(), nullable=True),
                    sa.Column('detection_last_at', sa.DateTime(), nullable=True),
                    sa.Column('detection_num', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('crtsh_input',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('sld_id', sa.BigInteger(), nullable=True),
                    sa.Column('iquery', sa.String(length=255), nullable=False),
                    sa.Column('itype', sa.SmallInteger(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['sld_id'], ['base_domain.id'], name='crtsh_input_base_domain_id'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_crtsh_input_sld_id'), 'crtsh_input', ['sld_id'], unique=False)
    op.create_unique_constraint('crtsh_input_key_unique', 'crtsh_input', ['iquery', 'itype'])

    op.create_table('subdomain_watch_target',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('scan_host', sa.String(length=255), nullable=False),
                    sa.Column('scan_ports', sa.Text(), nullable=True),
                    sa.Column('top_domain_id', sa.BigInteger(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('last_scan_at', sa.DateTime(), nullable=True),
                    sa.Column('last_scan_state', sa.SmallInteger(), nullable=True),
                    sa.ForeignKeyConstraint(['top_domain_id'], ['base_domain.id'], name='sub_wt_base_domain_id'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_subdomain_watch_target_top_domain_id'), 'subdomain_watch_target', ['top_domain_id'],
                    unique=False)

    op.create_table('subdomain_results',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('watch_id', sa.BigInteger(), nullable=False),
                    sa.Column('scan_type', sa.SmallInteger(), nullable=True),
                    sa.Column('scan_status', sa.SmallInteger(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('last_scan_at', sa.DateTime(), nullable=True),
                    sa.Column('last_scan_idx', sa.BigInteger(), nullable=True),
                    sa.Column('num_scans', sa.Integer(), nullable=True),
                    sa.Column('result', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['watch_id'], ['subdomain_watch_target.id'], name='wa_sub_res_watch_target_id'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_subdomain_results_watch_id'), 'subdomain_results', ['watch_id'], unique=False)

    op.create_table('user_subdomain_watch_target',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', mysql.INTEGER(display_width=10, unsigned=True), nullable=False),
                    sa.Column('watch_id', sa.BigInteger(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('deleted_at', sa.DateTime(), nullable=True),
                    sa.Column('disabled_at', sa.DateTime(), nullable=True),
                    sa.Column('auto_scan_added_at', sa.DateTime(), nullable=True),
                    sa.Column('scan_periodicity', sa.BigInteger(), nullable=True),
                    sa.Column('scan_type', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='wa_sub_users_id'),
                    sa.ForeignKeyConstraint(['watch_id'], ['subdomain_watch_target.id'], name='wa_sub_watch_target_id'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id', 'watch_id', name='wa_user_sub_watcher_uniqe')
                    )
    op.create_index(op.f('ix_user_subdomain_watch_target_user_id'), 'user_subdomain_watch_target', ['user_id'],
                    unique=False)
    op.create_index(op.f('ix_user_subdomain_watch_target_watch_id'), 'user_subdomain_watch_target', ['watch_id'],
                    unique=False)

    op.add_column(u'crtsh_query', sa.Column('certs_sh_ids', sa.Text(), nullable=True))
    op.add_column(u'crtsh_query', sa.Column('input_id', sa.BigInteger(), nullable=True))
    op.add_column(u'crtsh_query', sa.Column('newest_cert_id', sa.BigInteger(), nullable=True))
    op.add_column(u'crtsh_query', sa.Column('newest_cert_sh_id', sa.BigInteger(), nullable=True))
    op.add_column(u'crtsh_query', sa.Column('sub_watch_id', sa.BigInteger(), nullable=True))

    op.create_index(op.f('ix_crtsh_query_input_id'), 'crtsh_query', ['input_id'], unique=False)
    op.create_index(op.f('ix_crtsh_query_sub_watch_id'), 'crtsh_query', ['sub_watch_id'], unique=False)

    op.create_foreign_key('crtsh_watch_input_id', 'crtsh_query', 'crtsh_input', ['input_id'], ['id'])
    op.create_foreign_key('crtsh_watch_sub_target_id', 'crtsh_query', 'subdomain_watch_target', ['sub_watch_id'],
                          ['id'])

    op.add_column(u'user_watch_target', sa.Column('auto_scan_added_at', sa.DateTime(), nullable=True))
    op.add_column(u'user_watch_target', sa.Column('disabled_at', sa.DateTime(), nullable=True))

    op.add_column('user_subdomain_watch_target', sa.Column('auto_fill_watches', sa.SmallInteger(), nullable=False,
                                                           server_default='0'))

    op.add_column('scan_handshakes', sa.Column('tls_alert_code', sa.Integer(), nullable=True))
    op.add_column('scan_handshakes', sa.Column('err_valid_ossl_code', sa.Integer(), nullable=True))
    op.add_column('scan_handshakes', sa.Column('err_valid_ossl_depth', sa.Integer(), nullable=True))

    op.add_column('certificates', sa.Column('key_bit_size', sa.Integer(), nullable=True))
    op.add_column('certificates', sa.Column('key_type', sa.SmallInteger(), nullable=True))
    op.add_column('certificates', sa.Column('sig_alg', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'user_watch_target', 'disabled_at')
    op.drop_column(u'user_watch_target', 'auto_scan_added_at')
    op.drop_constraint('crtsh_watch_sub_target_id', 'crtsh_query', type_='foreignkey')
    op.drop_constraint('crtsh_watch_input_id', 'crtsh_query', type_='foreignkey')
    op.drop_constraint('wa_sub_users_id', 'user_subdomain_watch_target', type_='foreignkey')
    op.drop_constraint('wa_sub_watch_target_id', 'user_subdomain_watch_target', type_='foreignkey')
    op.drop_constraint('wa_sub_res_watch_target_id', 'subdomain_results', type_='foreignkey')
    op.drop_constraint('sub_wt_base_domain_id', 'subdomain_watch_target', type_='foreignkey')
    op.drop_constraint('crtsh_input_base_domain_id', 'crtsh_input', type_='foreignkey')
    op.drop_index(op.f('ix_crtsh_query_sub_watch_id'), table_name='crtsh_query')
    op.drop_index(op.f('ix_crtsh_query_input_id'), table_name='crtsh_query')
    op.drop_column(u'crtsh_query', 'sub_watch_id')
    op.drop_column(u'crtsh_query', 'newest_cert_sh_id')
    op.drop_column(u'crtsh_query', 'newest_cert_id')
    op.drop_column(u'crtsh_query', 'input_id')
    op.drop_column(u'crtsh_query', 'certs_sh_ids')
    op.drop_index(op.f('ix_user_subdomain_watch_target_watch_id'), table_name='user_subdomain_watch_target')
    op.drop_index(op.f('ix_user_subdomain_watch_target_user_id'), table_name='user_subdomain_watch_target')
    op.drop_table('user_subdomain_watch_target')
    op.drop_index(op.f('ix_subdomain_results_watch_id'), table_name='subdomain_results')
    op.drop_table('subdomain_results')
    op.drop_index(op.f('ix_subdomain_watch_target_top_domain_id'), table_name='subdomain_watch_target')
    op.drop_table('subdomain_watch_target')
    op.drop_index(op.f('ix_crtsh_input_sld_id'), table_name='crtsh_input')
    op.drop_table('crtsh_input')
    op.drop_table('subdomain_scan_blacklist')
    op.drop_column('scan_handshakes', 'tls_alert_code')
    op.drop_column('scan_handshakes', 'err_valid_ossl_depth')
    op.drop_column('scan_handshakes', 'err_valid_ossl_code')

    op.drop_column('certificates', 'sig_alg')
    op.drop_column('certificates', 'key_type')
    op.drop_column('certificates', 'key_bit_size')
    # ### end Alembic commands ###
