import os

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import datetime

import stdnum.ch.esr as stdnum_esr

from flask import render_template_string
from flask_mail import Message

from dotenv import load_dotenv


from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

load_dotenv('./env/mail.env')
mailDefaultSender = os.getenv("MAIL_DEFAULT_SENDER")
load_dotenv('./env/hitobito.env')
sender = os.getenv("HITOBITO_SENDER")

load_dotenv('./env/bank.env')
prefix = os.getenv('BANK_REF_PREFIX')
REF_NUM_LENGTH = 27

try:
    import hitobito
    import generate
except ImportError:
    pass

# Base for the SQL Schema


class BulkInvoice(Base):
    __tablename__ = "bulk_invoice"

    status = sa.Column(ENUM('created', 'issued', 'closed',
                       name='bulk_invoice_status'), nullable=False)

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Text)
    issuing_date = sa.Column(sa.TIMESTAMP)
    due_date = sa.Column(sa.TIMESTAMP)

    text_mail = sa.Column(sa.Text)
    text_invoice = sa.Column(sa.Text)
    text_reminder = sa.Column(sa.Text)

    create_time = sa.Column(
        sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    update_time = sa.Column(
        sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)

    # Define a property for the name with the relative address
    @hybrid_property
    def name(self):
        return "bulk/%s" % self.id

    # Define the SQL expression for this property in order to enable SQL queries using it
    @name.expression
    def name(cls):
        return sa.func.concat("bulk/", cls.id)

    def __init__(self, title, group_id, mailing_list_id, status='created', due_date=None, text_mail="{{ salutation }}, \n Dies ist eine Testmail\n Grüsse Pfnörch", text_invoice="{{ salutation }},\n Rechnungstext\n Grüsse Pfnörch", text_reminder="Reminder Text"):
        self.title = title
        self.status = status
        self.due_date = due_date
        self.text_mail = text_mail
        self.text_invoice = text_invoice
        self.text_reminder = text_reminder

        self.create_time = datetime.datetime.utcnow()
        self.update_time = self.create_time

        people = hitobito.getMailingListNameIDs(group_id=group_id, mailing_list_id=mailing_list_id)

        self.invoices = [Invoice(recipient, self.create_time.strftime(
            "%Y%m%d")) for recipient in people]

    # Create a property for the display name

    @hybrid_property
    def display_name(self):
        return self.title

    # Define the relationship between the BulkInvoice and its Invoices
    invoices = relationship("Invoice", back_populates="bulk_invoice")

    # Functions for interacting with the BulkInvoice
    def issue(self):
        # TODO: add functionality
        self.issuing_date = datetime.datetime.utcnow()
        self.due_date = self.issuing_date + datetime.timedelta(days=30)
        self.status = 'issued'

    def close(self):
        # TODO: add functionality
        self.status = 'closed'

    def get_messages(self, generator=False):
        if generator:
            return (invoice.get_message() for invoice in self.invoices)
        else:
            return [invoice.get_message() for invoice in self.invoices]

    def generate(self, generator=False):
        if generator:
            return (invoice.generate() for invoice in self.invoices)
        else:
            return [invoice.generate() for invoice in self.invoices]

    def __repr__(self):
        return "<BulkInvoice(id=%s, title=%s,status=%s, issuing_date=%s, due_date=%s, len(invoices)=%s, create_time=%s, update_time=%s, text_invoice=%s(...), text_reminder=%s(...))>" % (
            self.id, self.title, self.status, self.issuing_date, self.due_date, len(self.invoices), self.create_time, self.update_time, str(self.text_invoice)[0:5], str(self.text_reminder)[0:5])


# Base for the SQL Schema
class Invoice(Base):
    __tablename__ = "invoice"

    id = sa.Column(sa.Integer, primary_key=True)

    bulk_invoice_id = sa.Column(sa.Integer, sa.ForeignKey(
        "bulk_invoice.id"), nullable=False)

    esr = sa.Column(sa.String(length=27), unique=True)

    status = sa.Column(ENUM('pending', 'paid', 'annulled',
                       name='invoice_status'), nullable=False)
    status_message = sa.Column(sa.Text)

    recipient = sa.Column(sa.Integer)
    recipient_name = sa.Column(sa.Text)

    create_time = sa.Column(
        sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)
    update_time = sa.Column(
        sa.TIMESTAMP, server_default=sa.func.now(), nullable=False)

    def __init__(self, recipient, datestring, status='pending', status_message="Status Message"):
        self.recipient = recipient['id']
        self.recipient_name = recipient['name']

        self.status = status
        self.status_message = status_message
        # generate reference number
        end = str(self.recipient) + "000" + datestring
        no_check_digit = prefix + \
            ("0"*(REF_NUM_LENGTH-len(prefix)-len(end)-1)) + end
        self.esr = no_check_digit + stdnum_esr.calc_check_digit(no_check_digit)


    # Define a property for the name with the relative address
    @hybrid_property
    def name(self):
        return "bulk/%s/invoices/%s" % self.bulk_invoice_id, self.id

    # Define the SQL expression for this synonym in order to enable queries using it
    @name.expression
    def name(cls):
        return sa.func.concat("bulk/", cls.bulk_invoice_id, "/invoices/", cls.id)

    @hybrid_property
    def mail_body(self):
        return render_template_string(self.bulk_invoice.text_mail, salutation=hitobito.getPerson(self.recipient)['salutation'])

    @hybrid_property
    def invoice_body(self):
        return render_template_string(self.bulk_invoice.text_invoice, salutation=hitobito.getPerson(self.recipient)['salutation'])

    @hybrid_property
    def reminder_body(self):
        return render_template_string(self.bulk_invoice.text_reminder, salutation=hitobito.getPerson(self.recipient)['salutation'])

    # Define the relationship between the Invoice and its BulkInvoice
    bulk_invoice = relationship("BulkInvoice", back_populates="invoices")

    def generate(self):
        if(self.bulk_invoice.status != 'issued'):
            raise NotIssued(self.bulk_invoice.status)
        
        string = generate.invoicePDF(title=self.bulk_invoice.title, text_body=self.invoice_body, account=os.getenv("BANK_IBAN"), creditor={
            'name': 'Pfadfinderkorps Flamberg', 'pcode': '8070', 'city': 'Zürich', 'country': 'CH',
        }, ref=self.esr, hitobito_debtor=hitobito.getPerson(self.recipient), hitobito_sender=hitobito.getPerson(sender), date=self.bulk_invoice.issuing_date, due_date=self.bulk_invoice.due_date)

        return string

    def get_message(self):

        msg = Message("Subject", bcc=[mailDefaultSender])
        msg.add_recipient(hitobito.getPerson(self.recipient)['emails'][0])

        msg.body = self.mail_body
        msg.attach("Rechnung.pdf", "application/pdf", self.generate())
        return msg

    def __repr__(self):
        return "<Invoice(id=%s, status=%s, status_message=%s(...), recipient=%s, recipient_name=%s, bulk_invoice=%s, create_time=%s, update_time=%s)>" % (
            self.id, self.status, str(self.status_message)[0:5], self.recipient, self.recipient_name, self.bulk_invoice_id, self.create_time, self.update_time)


# Exceptions
class NotIssued(Exception):
    def __init__(self, status):
        self.status = status
        