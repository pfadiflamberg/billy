import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sapsql
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class BulkInvoice(Base):
    __tablename__ = "bulk_invoice"

    status = sa.Column(sapsql.ENUM('created', 'issued', 'closed', name='bulk_invoice_status'))


    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Text)
    issuing_date = sa.Column(sa.TIMESTAMP)
    due_date = sa.Column(sa.TIMESTAMP)

    text_invoice = sa.Column(sa.Text)
    text_reminder = sa.Column(sa.Text)

    create_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    update_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)

    invoices = relationship("Invoice", back_populates = "bulk_invoice")

    def __repr__(self):
        return "<BulkInvoice(id=%s, title=%s,status=%s, issuing_date=%s, due_date=%s, len(invoices)=%s, create_time=%s, update_time=%s, text_invoice=%s(...), text_reminder=%s(...))>" % (
                                self.id, self.title, self.status, self.issuing_date, self.due_date, len(self.invoices), self.create_time, self.update_time, str(self.text_invoice)[0:5], str(self.text_reminder)[0:5])


class Invoice(Base):
    __tablename__ = "invoice"

    id = sa.Column(sa.Integer, primary_key=True)

    bulk_invoice_id = sa.Column(sa.Integer, sa.ForeignKey("bulk_invoice.id"), nullable = False)

    status = sa.Column(sapsql.ENUM('pending', 'paid', 'annulled', name='invoice_status'))
    status_message = sa.Column(sa.Text)

    recipient = sa.Column(sa.Integer)
    recipient_name = sa.Column(sa.Text)

    create_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    update_time = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    
    bulk_invoice = relationship("BulkInvoice", back_populates="invoices")

    def __repr__(self):
        return "<Invoice(id=%s, status=%s, status_message=%s(...), recipient=%s, recipient_name=%s, bulk_invoice=%s, create_time=%s, update_time=%s)>" % (
                                self.id, self.status, str(self.status_message)[0:5], self.recipient, self.recipient_name, self.bulk_invoice_id, self.create_time, self.update_time)