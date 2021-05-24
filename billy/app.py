from dotenv import load_dotenv
import os

from model import Invoice, BulkInvoice, NotIssued
import db

from loguru import logger

import zipfile
import io
from requests import HTTPError, ConnectionError

from flask import Flask, request, jsonify, make_response, send_file, g
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_marshmallow.sqla import HyperlinkRelated
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field

from flask_mail import Mail, email_dispatched
from smtplib import SMTPException
from flask_cors import CORS

# init
app = Flask(__name__)
CORS(app)

load_dotenv('./env/mail.env')

mailServer = os.getenv('MAIL_SERVER')
mailPort = os.getenv('MAIL_PORT')
mailUseTLS = bool(int(os.getenv('MAIL_USE_TLS')))
mailUseSSL = bool(int(os.getenv('MAIL_USE_SSL')))
mailUsername = os.getenv('MAIL_USERNAME')
mailDefaultSender = os.getenv('MAIL_DEFAULT_SENDER')
mailPassword = os.getenv('MAIL_PASSWORD')

app.config['MAIL_SERVER'] = mailServer
app.config['MAIL_PORT'] = mailPort
app.config['MAIL_USE_TLS'] = mailUseTLS
app.config['MAIL_USE_SSL'] = mailUseSSL
app.config['MAIL_USERNAME'] = mailUsername
app.config['MAIL_DEFAULT_SENDER'] = mailDefaultSender
app.config['MAIL_PASSWORD'] = mailPassword
app.config['MAIL_DEBUG'] = True
# Must be true unless you actually want to send emails
app.config['MAIL_SUPPRESS_SEND'] = True

mail = Mail(app)


def log_message(message, app):
    logger.info("Sent to: {recipient} with CC: {cc} and BCC: {bcc}",
                recipient=message.recipients, cc=message.cc, bcc=message.bcc)


email_dispatched.connect(log_message)

ma = Marshmallow(app)


class InvoiceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Invoice


# Create the Schemas for Invoices and lists of them
invoiceSchema = InvoiceSchema()
invoicesSchema = InvoiceSchema(many=True)


class BulkInvoiceSchema(SQLAlchemySchema):
    class Meta:
        model = BulkInvoice

    # Define the relevant fields for JSON
    name = fields.Str()
    display_name = fields.Str()
    issuing_date = auto_field()
    due_date = auto_field()
    text_invoice = auto_field()
    text_reminder = auto_field()


# Create the Schemas for BulkInvoices and lists of them
bulkInvoiceSchema = BulkInvoiceSchema()
bulkInvoicesSchema = BulkInvoiceSchema(many=True)

@app.errorhandler(Exception)
def handle_unhandled(e):
    # Handle all others for now
    return make_response(jsonify(code=500, reason=type(e).__name__), 500)

@app.errorhandler(ConnectionError)
def handle_connection_error(e):
    return make_response(jsonify(code=500, reason="Internal Server Error: Could not connect to hitobito"), 500)

@app.errorhandler(HTTPError)
def handle_http_error(e):
    # If 404: The group does not exist (hitobito-URL could also be invalid) -> 409 Invalid argument
    # Else: Something with the HTTP response was wrong -> 500 or 502
    """Return JSON instead of HTML for HTTP errors."""
    logger.debug("request: {request}, response: {response}, data: {data}",
                request=e.request.url, response=e.response, data=e.response.content)
    if e.response.status_code == 404:
        response=make_response(jsonify(code=409, reason="Invalid Argument: Group does not exist"), 409)
    else:
        response = make_response(jsonify(code=500, reason="Internal Server Error: Bad Answer to HTTP Request", http_reason=e.response.reason, http_code=e.response.status_code, url=e.request.url), 500)
    return response

@app.errorhandler(KeyError)
def handle_key_error(e):
    # Missing Parameter -> 409 to be like restify, 400 would make more sense
    return make_response(jsonify(code=409, reason="Missing Parameter", missing_parameter=e.args[0]), 409)

@app.errorhandler(NotIssued)
def handle_not_issued(e):
    # Request was ok, but conflicts with resource state -> Invalid Argument
    return make_response(jsonify(code=409, reason="Invalid Argument: Invoice has not been issued or already been closed", invoice_status=e.status), 409)

@app.errorhandler(SMTPException)
def handle_mail_error(e):
    # Clients request was fine, but could not contact smtp/send mail -> 500
    return make_response(jsonify(code=500, reason="Internal Server Error: SMTP", smtp_code=e.smtp_code, smtp_error=e.smtp_error.decode("utf-8")), 500)

@app.errorhandler(db.ResourceNotFound)
def handle_resource_not_found(e):
    # Resource not in database -> 404
    return make_response(jsonify(code=404, reason="Not Found"), 404)

@app.before_first_request
def upgradeDB(version="head"):
    db.upgradeDatabase(version)

@app.before_request
def getSession():
    g.session = db.loadSession()

@app.teardown_request
def closeSession(_):
    try:
        g.session.close()
    except:
        logger.log("Could not close session")



@app.route('/bulk', methods=['POST'])
def addBulkInvoice():
    session = g.session

    # Get the 'group' parameter
    title = request.json['title']
    group = request.json['group']

    # Create add, and commit the new bulk invoice to get the id
    newBI = BulkInvoice(title=title, group_id=group)
    session.add(newBI)
    session.commit()

    res = jsonify(bulkInvoiceSchema.dump(newBI))
    return res


@app.route('/bulk/<id>', methods=['GET'])
def getBulkInvoice(id):
    session = g.session

    # jsonify the dump of the bulk invoice
    res = jsonify(bulkInvoiceSchema.dump(db.getBulkInvoice(session, id)))
    return res


@app.route('/bulk/', methods=['GET'])
def getBulkInvoices():
    session = g.session

    # jsonify the dump of the list of invoices
    res = jsonify(items=bulkInvoicesSchema.dump(
        db.getBulkInvoiceList(session)))
    return res


@app.route('/bulk/<id>', methods=['PUT'])
def updateBulkInvoice(id):
    session = g.session

    # Get BulkInvoice
    bi = db.getBulkInvoice(session, id)

    # Get json paramters, default to old if not supplied
    text_mail = request.json.get('text_mail', bi.text_mail)
    text_invoice = request.json.get('text_invoice', bi.text_invoice)
    text_reminder = request.json.get('text_reminder', bi.text_reminder)
    title = request.json.get('title', bi.title)

    # Update the attributes
    bi.text_mail = text_mail
    bi.text_invoice = text_invoice
    bi.text_reminder = text_reminder
    bi.title = title

    # Dump the data, commit and close the session
    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    return res


@app.route('/bulk/<id>:issue', methods=['POST'])
def issueBulkInvoice(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)
    if bi.status != 'issued':
        bi.issue()

    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    return res


@app.route('/bulk/<id>:close', methods=['POST'])
def closeBulkInvoice(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)
    bi.close()

    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    return res


@app.route('/bulk/<id>:send', methods=['POST'])
def sendBulkInvoice(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)

    for msg in bi.get_messages(True):
        mail.send(msg)

    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    return res


@app.route('/bulk/<id>:generate', methods=['POST'])
def generateBulkInvoice(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)

    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for invoice in bi.invoices:
            name = invoice.recipient_name + ".pdf"
            pdf = invoice.generate()
            z.writestr(name, pdf)
    data.seek(0)

    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='data.zip'
    )


@app.route('/bulk/<bulk_id>/invoices/<id>', methods=['GET'])
def getInvoice(bulk_id, id):
    session = g.session

    # jsonify the dump of the bulk invoice
    res = jsonify(invoiceSchema.dump(db.getInvoice(session, id)))
    return res


@app.route('/bulk/<id>/invoices', methods=['GET'])
def getInvoices(id):
    session = g.session

    # jsonify the dump of the list of invoices
    res = jsonify(items=invoicesSchema.dump(db.getInvoiceList(session, id)))
    return res


@app.route('/bulk/<bulk_id>/invoices/<id>', methods=['PUT'])
def updateInvoice(bulk_id, id):
    session = g.session

    # Get Invoice
    invoice = db.getInvoice(session, id)

    # Get json paramsk
    status = request.json.get('status', invoice.status)
    status_message = request.json.get('status_message', invoice.status_message)

    invoice.status = status
    invoice.status_message = status_message

    res = jsonify(invoiceSchema.dump(invoice))
    session.commit()
    return res


@app.route('/bulk/<bulk_id>/invoices/<id>:generate', methods=['POST'])
def generateInvoice(bulk_id, id):
    session = g.session

    invoice = db.getInvoice(session, id)

    binary_pdf = invoice.generate()
    response = make_response(binary_pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'invoice'

    return response


@app.route('/bulk/<bulk_id>/invoices/<id>/mail', methods=['POST'])
def getMailBody(bulk_id, id):
    session = g.session

    invoice = db.getInvoice(session, id)
    msg = invoice.get_message()
    mail.send(msg)
    res=jsonify(invoiceSchema.dump(invoice))
    
    return res


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
