import sqlalchemy as sa
from sqlalchemy import create_engine
import sqlalchemy.dialects.postgresql as sapsql

engine_string = "postgresql+psycopg2://postgres:password@billy-postgres:5432/billy"
engine = create_engine(engine_string,echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class BulkInvoice(Base):
    __tablename__ = "bulk_invoice"

    state = sa.Column(sapsql.ENUM('created', 'issued', 'closed', name='bulk_invoice_state'))


    id = sa.Column(sa.Integer, primary_key=True)
    issuing_date = sa.Column(sa.TIMESTAMP)
    due_date = sa.Column(sa.TIMESTAMP)

    text_invoice = sa.Column(sa.Text)
    text_reminder = sa.Column(sa.Text)

    create_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    update_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)

class Invoice(Base):
    __tablename__ = "invoice"

    id = sa.Column(sa.Integer, primary_key=True)

    bulk_invoice_id = sa.Column(sa.Integer, sa.ForeignKey("bulk_invoice.id"), nullable = False)

    state = sa.Column(sapsql.ENUM('pending', 'paid', 'annulled', name='invoice_state'))
    state_message = sa.Column(sa.Text)

    recipient = sa.Column(sa.Integer)
    recipient_name = sa.Column(sa.Text)

    create_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    update_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    