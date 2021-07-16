import os
import db
import secrets
import zipfile
import io

from model import Invoice, BulkInvoice, NotIssued
from loguru import logger
from requests import HTTPError, ConnectionError
from http import HTTPStatus
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response, redirect, send_file, g, url_for, make_response
from flask_marshmallow import Marshmallow
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field
from flask_mail import Mail, email_dispatched
from smtplib import SMTPException
from flask_cors import CORS

load_dotenv('./env/hitobito.env')
load_dotenv('./env/server.env')
load_dotenv('./env/mail.env')

HITOBITO_BASE = os.getenv('HITOBITO_HOST')
UNPROTECTED_PATH = '/oauth'

dance = OAuth2ConsumerBlueprint(
    "billy", __name__,
    client_id=os.getenv('HITOBITO_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('HITOBITO_OAUTH_SECRET'),
    base_url=HITOBITO_BASE,
    token_url="{base}/oauth/token".format(base=HITOBITO_BASE),
    authorization_url="{base}/oauth/authorize".format(base=HITOBITO_BASE),
    redirect_url=os.getenv('REDIRECT_URL_LOGIN'),
    scope=['email', 'name', 'with_roles', 'api', 'openid']
)

# init
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
app.register_blueprint(dance, url_prefix=UNPROTECTED_PATH)
CORS(app, origins=os.getenv('CLIENT_ORIGIN').split(
    ','), supports_credentials=True)

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

    # Define the relevant fields for JSON
    name = fields.Str()
    update_time = auto_field()
    status = auto_field()
    status_message = auto_field()
    recipient = auto_field()
    recipient_name = auto_field()
    esr = auto_field()


# Create the Schemas for Invoices and lists of them
invoiceSchema = InvoiceSchema()
invoicesSchema = InvoiceSchema(many=True)


class BulkInvoiceSchema(SQLAlchemySchema):
    class Meta:
        model = BulkInvoice

    # Define the relevant fields for JSON
    name = fields.Str()
    display_name = fields.Str()
    mailing_list = auto_field()
    issuing_date = auto_field()
    update_time = auto_field()
    due_date = auto_field()
    status = auto_field()
    text_invoice = auto_field()
    text_reminder = auto_field()
    text_mail = auto_field()


# Create the Schemas for BulkInvoices and lists of them
bulkInvoiceSchema = BulkInvoiceSchema()
bulkInvoicesSchema = BulkInvoiceSchema(many=True)


@app.errorhandler(ConnectionError)
def handle_connection_error(e):
    return make_response(jsonify(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=HTTPStatus.INTERNAL_SERVER_ERROR.phrase + ": Could not connect to hitobito"), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.errorhandler(Exception)
def handle_exception_error(e):
    logger.info(e)
    if e == HTTPStatus.FORBIDDEN:
        return make_response(jsonify(code=HTTPStatus.FORBIDDEN, message=HTTPStatus.FORBIDDEN.phrase + ": User not allowed to use application."), HTTPStatus.FORBIDDEN)
    return "What are you doing? You are not allowed to use this application."


@app.errorhandler(HTTPError)
def handle_http_error(e):
    # If HTTPStatus.NOT_FOUND: The group does not exist (hitobito-URL could also be invalid) -> HTTPStatus.BAD_REQUEST Invalid argument
    # Else: Something with the HTTP response was wrong -> HTTPStatus.INTERNAL_SERVER_ERROR or 502
    """Return JSON instead of HTML for HTTP errors."""
    logger.debug("request: {request}, response: {response}, data: {data}",
                 request=e.request.url, response=e.response, data=e.response.content)
    if e.response.status_code == HTTPStatus.NOT_FOUND:
        response = make_response(jsonify(
            code=HTTPStatus.BAD_REQUEST, message="Invalid Argument: Group does not exist"), HTTPStatus.BAD_REQUEST)
    else:
        response = make_response(jsonify(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=HTTPStatus.INTERNAL_SERVER_ERROR.phrase + ": Bad Answer to HTTP Request",
                                 details={"http_reason": e.response.reason, "http_code": e.response.status_code, "url": e.request.url}), HTTPStatus.INTERNAL_SERVER_ERROR)
    return response


@app.errorhandler(KeyError)
def handle_key_error(e):
    # Missing Parameter -> HTTPStatus.BAD_REQUEST
    return make_response(jsonify(code=HTTPStatus.BAD_REQUEST, message="Missing Parameter", details={"missing_parameter": e.args[0]}), HTTPStatus.BAD_REQUEST)


@app.errorhandler(NotIssued)
def handle_not_issued(e):
    # Request was ok, but conflicts with resource state -> Invalid Argument
    return make_response(jsonify(code=HTTPStatus.BAD_REQUEST, message="Invalid Argument: Invoice has not been issued or already been closed", invoice_status=e.status), HTTPStatus.BAD_REQUEST)


@app.errorhandler(SMTPException)
def handle_mail_error(e):
    # Clients request was fine, but could not contact smtp/send mail -> HTTPStatus.INTERNAL_SERVER_ERROR
    return make_response(jsonify(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=HTTPStatus.INTERNAL_SERVER_ERROR.phrase + ": SMTP", details={"smtp_code": e.smtp_code, "smtp_error": e.smtp_error.decode("utf-8")}), HTTPStatus.INTERNAL_SERVER_ERROR)


@app.errorhandler(db.ResourceNotFound)
def handle_resource_not_found(e):
    # Resource not in database -> HTTPStatus.NOT_FOUND
    return make_response(jsonify(code=HTTPStatus.NOT_FOUND, message=HTTPStatus.NOT_FOUND.phrase), HTTPStatus.NOT_FOUND)


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
    mailing_list = request.json['mailing_list']

    # Create add, and commit the new bulk invoice to get the id
    newBI = BulkInvoice(title=title, mailing_list=mailing_list)
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
    if bi.status == 'closed':
        return make_response(jsonify(code=HTTPStatus.METHOD_NOT_ALLOWED, message="Closed bulks can no longer be updated."), HTTPStatus.METHOD_NOT_ALLOWED)

    # Get json paramters, default to old if not supplied
    title = request.json.get('title', bi.title)
    mailing_list = request.json.get('mailing_list', bi.mailing_list)
    text_mail = request.json.get('text_mail', bi.text_mail)
    text_invoice = request.json.get('text_invoice', bi.text_invoice)
    text_reminder = request.json.get('text_reminder', bi.text_reminder)

    if bi.status == 'issued':
        if bi.mailing_list != mailing_list:
            return make_response(jsonify(code=HTTPStatus.BAD_REQUEST, message="The mailing list of an issued bulk can not be changed."), HTTPStatus.BAD_REQUEST)

    # Update the attributes
    bi.title = title
    bi.mailing_list = mailing_list
    bi.text_mail = text_mail
    bi.text_invoice = text_invoice
    bi.text_reminder = text_reminder

    # Dump the data, commit and close the session
    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    return res


@app.route('/bulk/<id>:issue', methods=['POST'])
def issueBulkInvoice(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)
    if bi.status != 'draft':
        return make_response(jsonify(code=HTTPStatus.METHOD_NOT_ALLOWED, message=HTTPStatus.METHOD_NOT_ALLOWED.phrase), HTTPStatus.METHOD_NOT_ALLOWED)

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


@app.route('/bulk/<id>/invoice', methods=['GET'])
def getInvoices(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)
    if bi.status == 'draft':
        return make_response(jsonify(code=HTTPStatus.METHOD_NOT_ALLOWED, message=HTTPStatus.METHOD_NOT_ALLOWED.phrase + ": bulk needs to be issued."), HTTPStatus.METHOD_NOT_ALLOWED)

    # jsonify the dump of the list of invoices
    res = jsonify(items=invoicesSchema.dump(db.getInvoiceList(session, id)))
    return res


@app.route('/bulk/<bulk_id>/invoice/<id>', methods=['GET'])
def getInvoice(bulk_id, id):
    session = g.session

    # jsonify the dump of the bulk invoice
    res = jsonify(invoiceSchema.dump(db.getInvoice(session, id)))
    return res


@app.route('/bulk/<bulk_id>/invoice/<id>', methods=['PUT'])
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


@app.route('/bulk/<bulk_id>/invoice/<id>.pdf', methods=['GET'])
def generateInvoice(bulk_id, id):
    session = g.session

    invoice = db.getInvoice(session, id)

    binary_pdf = invoice.generate()
    response = make_response(binary_pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=%s.pdf' % 'invoice'

    return response


@app.route('/bulk/<bulk_id>/invoice/<id>/mail', methods=['POST'])
def getMailBody(bulk_id, id):
    session = g.session

    invoice = db.getInvoice(session, id)
    msg = invoice.get_message()
    mail.send(msg)
    res = jsonify(invoiceSchema.dump(invoice))

    return res


@app.route('{path}/login'.format(path=UNPROTECTED_PATH))
def login():
    if not dance.session.authorized:
        return redirect(url_for('billy.login'))


@app.before_request
def check():
    if request.method == 'OPTIONS':  # preflight requests
        return
    if request.path.startswith(UNPROTECTED_PATH):
        return
    if not dance.session.authorized:
        return make_response(
            jsonify(code=HTTPStatus.UNAUTHORIZED, message=HTTPStatus.UNAUTHORIZED.phrase), HTTPStatus.UNAUTHORIZED)


@oauth_authorized.connect
def handle_login(blueprint, token):
    # make sure the user is allowed to access the site before giving out a tokens
    response = blueprint.session.get(
        'oauth/profile', headers={'X-Scope': 'with_roles'})
    role_ids = [x['group_id'] for x in response.json()['roles']]

    if int(os.getenv('HITOBITO_GROUP')) not in role_ids:
        raise Exception(HTTPStatus.FORBIDDEN)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
