import db
import secrets
import zipfile
import io
import error
import env

from PyPDF2 import PdfFileMerger, PdfFileReader
from model import Invoice, BulkInvoice
from loguru import logger
from requests import HTTPError, ConnectionError
from http import HTTPStatus
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response, redirect, send_file, g, url_for, make_response
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field
from flask_mail import Mail, email_dispatched
from smtplib import SMTPException
from flask_cors import CORS
import traceback
from sqlalchemy.orm import exc
import oauth

load_dotenv('./env/mail.env')


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = env.REDIRECT_URL_LOGIN.split(':')[0]
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


# init
app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.secret_key = secrets.token_urlsafe(32)
app.register_blueprint(oauth.dance, url_prefix=oauth.UNPROTECTED_PATH)
CORS(app, origins=env.CLIENT_ORIGIN.split(
    ','), supports_credentials=True)

mailServer = env.get('MAIL_SERVER')
mailPort = env.get('MAIL_PORT')
mailUseTLS = bool(int(env.get('MAIL_USE_TLS')))
mailUseSSL = bool(int(env.get('MAIL_USE_SSL')))
mailUsername = env.get('MAIL_USERNAME')
mailDefaultSender = env.get('MAIL_DEFAULT_SENDER')
mailPassword = env.get('MAIL_PASSWORD')

app.config['MAIL_SERVER'] = mailServer
app.config['MAIL_PORT'] = mailPort
app.config['MAIL_USE_TLS'] = mailUseTLS
app.config['MAIL_USE_SSL'] = mailUseSSL
app.config['MAIL_USERNAME'] = mailUsername
app.config['MAIL_DEFAULT_SENDER'] = mailDefaultSender
app.config['MAIL_PASSWORD'] = mailPassword
app.config['MAIL_DEBUG'] = False
# Must be true unless you actually want to send emails
app.config['MAIL_SUPPRESS_SEND'] = False

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
    last_email_sent = auto_field()
    esr = auto_field()


# Create the Schemas for Invoices and lists of them
invoiceSchema = InvoiceSchema()
invoicesSchema = InvoiceSchema(many=True)


class BulkInvoiceSchema(SQLAlchemySchema):
    class Meta:
        model = BulkInvoice

    # Define the relevant fields for JSON
    name = fields.Str()
    title = fields.Str()
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
    if isinstance(e, error.BillyError):
        return make_response(e.asJSON(), HTTPStatus.PRECONDITION_REQUIRED)
    logger.info(traceback.print_exc())
    return make_response(jsonify(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=HTTPStatus.INTERNAL_SERVER_ERROR.phrase + ": Error has been logged on the server."), HTTPStatus.INTERNAL_SERVER_ERROR)


@ app.errorhandler(HTTPError)
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


@ app.errorhandler(SMTPException)
def handle_mail_error(e):
    # Clients request was fine, but could not contact smtp/send mail -> HTTPStatus.INTERNAL_SERVER_ERROR
    return make_response(jsonify(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=HTTPStatus.INTERNAL_SERVER_ERROR.phrase + ": SMTP", details={"smtp_code": e.smtp_code, "smtp_error": e.smtp_error.decode("utf-8")}), HTTPStatus.INTERNAL_SERVER_ERROR)


@ app.errorhandler(db.ResourceNotFound)
def handle_resource_not_found(e):
    # Resource not in database -> HTTPStatus.NOT_FOUND
    return make_response(jsonify(code=HTTPStatus.NOT_FOUND, message=HTTPStatus.NOT_FOUND.phrase), HTTPStatus.NOT_FOUND)


@ app.before_first_request
def upgradeDB(version="head"):
    db.upgradeDatabase(version)


@ app.before_request
def getSession():
    g.session = db.loadSession()


@ app.teardown_request
def closeSession(_):
    try:
        g.session.close()
    except:
        logger.log("Could not close session")


@ app.route('/bulk', methods=['POST'])
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


@ app.route('/bulk/<id>', methods=['GET'])
def getBulkInvoice(id):
    session = g.session

    # jsonify the dump of the bulk invoice
    res = jsonify(bulkInvoiceSchema.dump(db.getBulkInvoice(session, id)))
    return res


@ app.route('/bulk/', methods=['GET'])
def getBulkInvoices():
    session = g.session

    # jsonify the dump of the list of invoices
    res = jsonify(items=bulkInvoicesSchema.dump(
        db.getBulkInvoiceList(session)))
    return res


@ app.route('/bulk/<id>', methods=['PUT'])
def updateBulkInvoice(id):
    session = g.session

    # Get BulkInvoice
    bi = db.getBulkInvoice(session, id)
    if bi.status != 'draft':
        return make_response(jsonify(code=HTTPStatus.METHOD_NOT_ALLOWED, message="A bulks can no longer be updated once it has been issued."), HTTPStatus.METHOD_NOT_ALLOWED)

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


@ app.route('/bulk/<id>:issue', methods=['POST'])
def issueBulkInvoice(id):
    logger.info('id: {id}'.format(id=id))
    session = g.session

    bi = db.getBulkInvoice(session, id)
    if bi.status != 'draft':
        return make_response(jsonify(code=HTTPStatus.METHOD_NOT_ALLOWED, message=HTTPStatus.METHOD_NOT_ALLOWED.phrase), HTTPStatus.METHOD_NOT_ALLOWED)

    bi.issue()
    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    return res


@ app.route('/bulk/<id>:close', methods=['POST'])
def closeBulkInvoice(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)
    bi.close()

    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    return res


@ app.route('/bulk/<id>:send', methods=['POST'])
def sendBulkInvoice(id):
    session = g.session

    force = bool(request.args.get('force', 0, type=int))
    skip = bool(request.args.get('skip', 0, type=int))

    mail_body = request.json['mail_body']

    bi = db.getBulkInvoice(session, id)
    sent_count = 0
    for success, result in bi.complete_messages(mail_body, generator=True, force=force, skip=skip):
        if success:
            mail.send(result)
            sent_count += 1

    res = jsonify(sent_count=sent_count)
    session.commit()
    return res


@ app.route('/bulk/<id>.zip', methods=['GET'])
def generateBulkInvoiceZip(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)

    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for name, string in bi.generate():
            name = name + ".pdf"
            z.writestr(name, string)
    data.seek(0)

    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='data.zip'
    )


@ app.route('/bulk/<id>.pdf', methods=['GET'])
def generateBulkInvoicePDF(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)

    data = io.BytesIO()
    merger = PdfFileMerger()
    for name, string in bi.generate():
        merger.append(PdfFileReader(io.BytesIO(string)))
    merger.write(data)
    data.seek(0)

    return send_file(
        data,
        mimetype='application/pdf',
        as_attachment=False,
        attachment_filename='data.pdf'
    )


@ app.route('/bulk/<id>/invoice', methods=['GET'])
def getInvoices(id):
    session = g.session

    bi = db.getBulkInvoice(session, id)
    if bi.status == 'draft':
        return make_response(jsonify(code=HTTPStatus.METHOD_NOT_ALLOWED, message=HTTPStatus.METHOD_NOT_ALLOWED.phrase + ": bulk needs to be issued."), HTTPStatus.METHOD_NOT_ALLOWED)

    # jsonify the dump of the list of invoices
    res = jsonify(items=invoicesSchema.dump(db.getInvoiceList(session, id)))
    return res


@ app.route('/bulk/<bulk_id>/invoice/<id>', methods=['GET'])
def getInvoice(bulk_id, id):
    session = g.session

    # jsonify the dump of the bulk invoice
    res = jsonify(invoiceSchema.dump(db.getInvoice(session, id)))
    return res


@ app.route('/bulk/<bulk_id>/invoice/<id>:annul', methods=['POST'])
def annulInvoice(bulk_id, id):
    session = g.session

    invoice = db.getInvoice(session, id)
    if invoice.status != 'pending':
        return make_response(jsonify(code=HTTPStatus.METHOD_NOT_ALLOWED, message=HTTPStatus.METHOD_NOT_ALLOWED.phrase + ": Only pending invoices can be annulled."), HTTPStatus.METHOD_NOT_ALLOWED)

    invoice.status = 'annulled'
    res = jsonify(invoiceSchema.dump(invoice))
    session.commit()
    return res


@ app.route('/bulk/<bulk_id>/invoice/<id>.pdf', methods=['GET'])
def generateInvoice(bulk_id, id):
    session = g.session

    invoice = db.getInvoice(session, id)
    invoice.bulk_invoice.prepare(skip=True)
    name, binary_pdf = invoice.generate()
    response = make_response(binary_pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % 'invoice'

    return response


@ app.route('/bulk/<bulk_id>/invoice/<id>:send', methods=['POST'])
def sendInvoice(bulk_id, id):
    session = g.session

    force = bool(request.args.get('force', 0, type=int))

    mail_body = request.json['mail_body']

    invoice = db.getInvoice(session, id)

    invoice.bulk_invoice.prepare()

    success, result = invoice.complete_message(mail_body, force=force)
    if success:
        mail.send(result)
    session.commit()
    return(jsonify(sent_time=invoice.last_email_sent.isoformat()))


@ app.route('/payment', methods=['POST'])
def uploadPayments():
    session = g.session
    payments = request.json['payments']
    updated_count = 0
    not_found = 0
    for p in payments:
        try:
            invoice = db.getInvoiceWithESR(session, p['esr'])
            if (invoice.status != 'paid'):
                invoice.status = 'paid'
                updated_count += 1
        except exc.NoResultFound:
            not_found += 1
    session.commit()
    return jsonify(marked_paid=updated_count, not_found=not_found)


@ app.route('{path}/login'.format(path=oauth.UNPROTECTED_PATH))
def login():
    if not oauth.dance.session.authorized:
        return redirect(url_for('billy.login'))


@ app.before_request
def check():
    if request.method == 'OPTIONS':  # preflight requests
        return
    if request.path.startswith(oauth.UNPROTECTED_PATH):
        return
    if not oauth.dance.session.authorized:
        return make_response(
            jsonify(code=HTTPStatus.UNAUTHORIZED, message=HTTPStatus.UNAUTHORIZED.phrase), HTTPStatus.UNAUTHORIZED)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
