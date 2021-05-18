from alembic import command
from alembic.config import Config
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import BulkInvoice, Invoice
# Use the environment variables to create the engine string

username = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PW')
address = os.getenv('MYSQL_SERVER')
port = os.getenv('MYSQL_PORT')
name = os.getenv('MYSQL_DB')

engine_string = "mysql+mysqldb://%s:%s@%s:%s/%s" % (
    username, password, address, port, name)
engine = create_engine(engine_string, echo=True)

# Create a sessionmaker
Session = sessionmaker(bind=engine)


# Read the config
alembic_cfg = Config('alembic.ini')

# Load and return a session to the billy database


def loadSession():
    """"""
    return Session()


# Functions to upgrade and downgrade to the specified version, if none specified: use head/base respectively

def upgradeDatabase(version="head"):
    command.upgrade(alembic_cfg, version)


def downgradeDatabase(version="base"):
    command.downgrade(alembic_cfg, version)

# Functions to access parts of the database


def getBulkInvoice(session, id):
    return session.query(BulkInvoice).get(id)


def getBulkInvoiceList(session):
    return session.query(BulkInvoice).all()


def getInvoice(session, id):
    return session.query(Invoice).get(id)


def getInvoiceList(session, id):
    return session.query(BulkInvoice).get(id).invoices
