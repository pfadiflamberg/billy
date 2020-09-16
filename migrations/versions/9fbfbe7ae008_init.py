"""init

Revision ID: 9fbfbe7ae008
Revises: 
Create Date: 2020-09-01 14:46:52.862756

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9fbfbe7ae008'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bulk_invoice',
    sa.Column('status', postgresql.ENUM('created', 'issued', 'closed', name='bulk_invoice_status'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('issuing_date', sa.TIMESTAMP(), nullable=True),
    sa.Column('due_date', sa.TIMESTAMP(), nullable=True),
    sa.Column('text_invoice', sa.Text(), nullable=True),
    sa.Column('text_reminder', sa.Text(), nullable=True),
    sa.Column('create_time', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bulk_invoice_id', sa.Integer(), nullable=False),
    sa.Column('status', postgresql.ENUM('pending', 'paid', 'annulled', name='invoice_status'), nullable=True),
    sa.Column('status_message', sa.Text(), nullable=True),
    sa.Column('recipient', sa.Integer(), nullable=True),
    sa.Column('recipient_name', sa.Text(), nullable=True),
    sa.Column('create_time', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bulk_invoice_id'], ['bulk_invoice.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invoice')
    op.drop_table('bulk_invoice')
    # ### end Alembic commands ###
    # handle types
    op.execute('drop type invoice_status')
    op.execute('drop type bulk_invoice_status')
