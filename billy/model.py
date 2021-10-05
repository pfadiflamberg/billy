import generate
import hitobito
import sqlalchemy as sa
import datetime
import stdnum.ch.esr as stdnum_esr
import env
import error

from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from loguru import logger
from flask import render_template_string
from flask_mail import Message
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

REF_NUM_LENGTH = 27

# Base for the SQL Schema


class BulkInvoice(Base):
    __tablename__ = "bulk_invoice"

    status = sa.Column(ENUM('draft', 'issued', 'closed',
                       name='bulk_invoice_status'), nullable=False)

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.Text)
    mailing_list = sa.Column(sa.Text)
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

    def __init__(self, title, mailing_list, status='draft', due_date=None,
                 text_mail="Hallo {{ recipient_shortname }}, \n Siehe Rechnung im Anahng.\n Liebe Grüsse {{ sender_shortname}}",
                 text_invoice="Hallo {{ recipient_shortname }},\n Rechnungstext\n Liebe Grüsse {{ sender_shortname}}",
                 text_reminder="Reminder Text"):
        self.title = title
        self.mailing_list = mailing_list
        self.status = status
        self.due_date = due_date
        self.text_mail = text_mail
        self.text_invoice = text_invoice
        self.text_reminder = text_reminder

        self.create_time = datetime.datetime.utcnow()
        self.update_time = self.create_time

    # Define the relationship between the BulkInvoice and its Invoices
    invoices = relationship("Invoice", back_populates="bulk_invoice")

    # Functions for interacting with the BulkInvoice
    def issue(self):
        # TODO: add functionality
        recipients = hitobito.getMailingListRecipients(self.mailing_list)
        self.invoices = [Invoice(hitobito.parseMailingListPerson(recipient, verify=False), self.create_time.strftime(
            "%Y%m%d"), self.id) for recipient in recipients.values()]

        self.issuing_date = datetime.datetime.utcnow()
        self.due_date = self.issuing_date + datetime.timedelta(days=30)

        self.status = 'issued'

    def close(self):
        # TODO: add functionality
        self.status = 'closed'

    def complete_messages(self, mail_body, generator=False, force=False, skip=False):
        self.prepare(skip=skip)

        if generator:
            return (invoice.complete_message(mail_body, force) for invoice in self.invoices if invoice.status == "pending")
        else:
            return [invoice.complete_message(mail_body, force) for invoice in self.invoices if invoice.status == "pending"]

    def prepare(self, skip=False):
        mailinglist_members = hitobito.getMailingListRecipients(
            self.mailing_list)
        # filter out new recipients that have been added to the mailing list after issuing
        active_ids = [invoice.recipient for invoice in self.invoices]
        self.people_list = dict(
            filter(lambda r: r[0] in active_ids, mailinglist_members.items()))  # recipients ^ mailinglist
        # List of all recipient ids that are no longer in the mailing list, but are not annulled yet.

        missing = [invoice for invoice in self.invoices
                   if invoice.recipient not in mailinglist_members.keys() and invoice.status == 'pending']
        inaccessible = []
        # fetch individual participants that are have been removed from the mailing list via ID
        for invoice in missing:
            returned_person = hitobito.getRawPerson(invoice.recipient)
            # If a person id is not accessible, hitobito will return a different person (the logged in user), check if this is the case
            if int(returned_person['id']) != invoice.recipient:
                inaccessible.append(invoice)
            else:
                self.people_list[invoice.recipient] = returned_person
        if len(inaccessible) > 0:
            raise error.InvoiceListError("Invoices not accessible",
                                         "Some recipients are no longer accessible, but their Invoices are still pending",
                                         [recipient.name for recipient in inaccessible])
        # parse all participents to make sure they are valid
        if not skip:
            issues = []
            for id in self.people_list:
                person = self.people_list[id]
                try:
                    hitobito.parseMailingListPerson(person)
                except error.BillyError as e:
                    issues.append(e)
            if len(issues) > 0:
                raise error.MultipleErrors(issues)
        self.user = hitobito.getUser()

    def cleanup(self):
        mailinglist_members = hitobito.getMailingListRecipients(
            self.mailing_list)
        missing = [invoice for invoice in self.invoices
                   if invoice.recipient not in mailinglist_members.keys() and invoice.status == 'pending']
        for invoice in missing:
            invoice.status = "annulled"
        return missing

    def generate(self, generator=False, skip=False):
        self.prepare(skip=skip)

        if generator:
            return (invoice.generate() for invoice in self.invoices if invoice.status == "pending")
        else:
            return [invoice.generate() for invoice in self.invoices if invoice.status == "pending"]

    def __repr__(self):
        return "<BulkInvoice(id=%s, title=%s, mailing_list=%s, status=%s, issuing_date=%s, due_date=%s, len(invoices)=%s, create_time=%s, update_time=%s, text_invoice=%s(...), text_reminder=%s(...))>" % (
            self.id, self.title, self.mailing_list, self.status, self.issuing_date, self.due_date, len(self.invoices), self.create_time, self.update_time, str(self.text_invoice)[0:5], str(self.text_reminder)[0:5])


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
    last_email_sent = sa.Column(
        sa.TIMESTAMP, server_default=None, nullable=True)

    def __init__(self, recipient, datestring, bulk_id, status='pending', status_message="Status Message"):
        self.recipient = recipient['id']
        self.recipient_name = recipient['name']

        logger.info("recipient_id: {id}, recipient_name: {name}".format(
            id=self.recipient, name=self.recipient_name))

        self.status = status
        self.status_message = status_message
        # generate reference number
        postfix = str(bulk_id) + datestring + str(self.recipient)
        logger.info("recipient_id: {id}, recipient_name: {name}, postfix: {postfix}".format(
            id=self.recipient, name=self.recipient_name, postfix=postfix))
        no_check_digit = env.BANK_REF_PREFIX + \
            ("0"*(REF_NUM_LENGTH-len(env.BANK_REF_PREFIX)-len(postfix)-1)) + postfix
        self.esr = no_check_digit + stdnum_esr.calc_check_digit(no_check_digit)

    # Define a property for the name with the relative address

    @hybrid_property
    def name(self):
        return "bulk/%s/invoice/%s" % (self.bulk_invoice_id, self.id)

    # Define the SQL expression for this synonym in order to enable queries using it
    @name.expression
    def name(cls):
        return sa.func.concat("bulk/", cls.bulk_invoice_id, "/invoice/", cls.id)

    def insert_variables(self, text):

        hitobito_debtor = hitobito.parseMailingListPerson(
            self.bulk_invoice.people_list[self.recipient], verify=False)
        hitobito_sender = self.bulk_invoice.user

        return render_template_string(text,
                                      title=self.bulk_invoice.title,
                                      due_date=self.bulk_invoice.due_date.strftime(
                                          '%d. %B %Y'),
                                      year_issued=self.bulk_invoice.issuing_date.strftime(
                                          '%Y'),
                                      date_issued=self.bulk_invoice.issuing_date.strftime(
                                          '%d. %B %Y'),
                                      recipient_name=hitobito_debtor['name'],
                                      recipient_shortname=hitobito_debtor['shortname'],
                                      sender_name=hitobito_sender['name'],
                                      sender_shortname=hitobito_sender['shortname'],
                                      )

    @hybrid_property
    def mail_body(self):
        return self.insert_variables(self.bulk_invoice.text_mail)

    @hybrid_property
    def invoice_body(self):
        if self.bulk_invoice.due_date.date() < datetime.datetime.utcnow().date():
            body = self.bulk_invoice.text_reminder
        else:
            body = self.bulk_invoice.text_invoice
        return self.insert_variables(body)

    @hybrid_property
    def reminder_body(self):
        return self.insert_variables(self.bulk_invoice.text_reminder)

    # Define the relationship between the Invoice and its BulkInvoice
    bulk_invoice = relationship("BulkInvoice", back_populates="invoices")

    def generate(self):
        if(self.bulk_invoice.status != 'issued'):
            raise error.InvoiceNotIssued(self.bulk_invoice)

        debtor = hitobito.parseMailingListPerson(
            self.bulk_invoice.people_list[self.recipient], verify=False)

        string = generate.invoicePDF(title=self.bulk_invoice.title, text_body=self.invoice_body, account=env.BANK_IBAN, creditor={
            'name': 'Pfadfinderkorps Flamberg', 'pcode': '8070', 'city': 'Zürich', 'country': 'CH',
        }, ref=self.esr, hitobito_debtor=debtor, hitobito_sender=self.bulk_invoice.user, date=datetime.datetime.utcnow(), date_issued=self.bulk_invoice.issuing_date, due_date=self.bulk_invoice.due_date)

        return debtor['name'], string

    def complete_message(self, mail_body, force=False):
        recently_sent = self.last_email_sent and datetime.datetime.utcnow(
        ) - self.last_email_sent < datetime.timedelta(days=30)
        if recently_sent and not force:
            logger.info("skip: mail sent in the last 30 days")
            return False, self
        recipient_emails = hitobito.parseMailingListPerson(
            self.bulk_invoice.people_list[self.recipient], verify=False)['emails']
        if len(recipient_emails) < 1:
            logger.info("skip: missing email address")
            return False, self
        msg = Message(self.bulk_invoice.title, recipients=recipient_emails, bcc=[
                      env.MAIL_DEFAULT_SENDER])

        # double new line for proper rendering in Apple Mail
        msg.body = self.insert_variables(mail_body) + "\n\n"
        _, string = self.generate()
        msg.attach("Rechnung.pdf", "application/pdf", string)
        self.last_email_sent = datetime.datetime.utcnow()
        return True, msg

    def __repr__(self):
        return "<Invoice(id=%s, status=%s, status_message=%s(...), recipient=%s, recipient_name=%s, bulk_invoice=%s, create_time=%s, update_time=%s)>" % (
            self.id, self.status, str(self.status_message)[0:5], self.recipient, self.recipient_name, self.bulk_invoice_id, self.create_time, self.update_time)
