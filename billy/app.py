import os

from model import Invoice, BulkInvoice
import db

from loguru import logger

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_marshmallow.sqla import HyperlinkRelated
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field

# init
app = Flask(__name__)

ma = Marshmallow(app)

# TODO: create proper schema


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


@app.route('/bulk', methods=['POST'])
def addBulkInvoice():
    session = db.loadSession()

    # Get the 'group' parameter
    group = request.json['group']

    # Create add, and commit the new bulk invoice to get the id
    newBI = BulkInvoice(group_id=group)
    session.add(newBI)
    session.commit()

    res = jsonify(bulkInvoiceSchema.dump(newBI))
    session.close()
    return res


@app.route('/bulk/<id>', methods=['GET'])
def getBulkInvoice(id):
    session = db.loadSession()

    # jsonify the dump of the bulk invoice
    res = jsonify(bulkInvoiceSchema.dump(db.getBulkInvoice(session, id)))
    session.close()
    return res


@app.route('/bulk/', methods=['GET'])
def getBulkInvoices():
    session = db.loadSession()

    # jsonify the dump of the list of invoices
    res = jsonify(bulkInvoicesSchema.dump(db.getBulkInvoiceList(session)))
    session.close()
    return res


@app.route('/bulk/<id>', methods=['PUT'])
def updateBulkInvoice(id):
    session = db.loadSession()

    # Get BulkInvoice
    bi = db.getBulkInvoice(session, id)

    # Get json paramters, default to old if not supplied
    text_invoice = request.json.get('text_invoice', bi.text_invoice)
    text_reminder = request.json.get('text_reminder', bi.text_reminder)

    # Update the attributes
    bi.text_invoice = text_invoice
    bi.text_reminder = text_reminder

    # Dump the data, commit and close the session
    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    session.close()
    return res


@app.route('/bulk/<id>:issue', methods=['POST'])
def issueBulkInvoice(id):
    session = db.loadSession()

    bi = db.getBulkInvoice(session, id)
    if bi.status != 'issued':
        bi.issue()

    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    session.close()
    return res


@app.route('/bulk/<id>:close', methods=['POST'])
def closeBulkInvoice(id):
    session = db.loadSession()

    bi = db.getBulkInvoice(session, id)
    bi.close()

    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    session.close()
    return res


@app.route('/bulk/<id>:send', methods=['POST'])
def sendBulkInvoice(id):
    session = db.loadSession()

    bi = db.getBulkInvoice(session, id)
    bi.send()

    res = jsonify(bulkInvoiceSchema.dump(bi))
    session.commit()
    session.close()
    return res


@app.route('/bulk/<id>:generate', methods=['POST'])
def generateBulkInvoice(id):
    session = db.loadSession()

    bi = db.getBulkInvoice(session, id)
    bi.generate()

    session.close()
    return "bulk_link"


@app.route('/bulk/<bulk_id>/invoices/<id>', methods=['GET'])
def getInvoice(bulk_id, id):
    session = db.loadSession()

    # jsonify the dump of the bulk invoice
    res = jsonify(invoiceSchema.dump(db.getInvoice(session, id)))
    session.close()
    return res


@app.route('/bulk/<id>/invoices', methods=['GET'])
def getInvoices(id):
    session = db.loadSession()

    # jsonify the dump of the list of invoices
    res = jsonify(invoicesSchema.dump(db.getInvoiceList(session, id)))
    session.close()
    return res


@app.route('/bulk/<bulk_id>/invoices/<id>:generate', methods=['POST'])
def generateInvoice(bulk_id, id):
    session = db.loadSession()

    invoice = db.getInvoice(session, id)
    invoice.generate()

    session.close()
    return "inv_link"


if __name__ == '__main__':
    app.run(debug=False)
