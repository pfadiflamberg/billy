import env

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import BulkInvoice, Invoice
# Use the environment variables to create the engine string

username = env.get('MYSQL_USER')
password = env.get('MYSQL_PW')
address = env.get('MYSQL_SERVER')
port = env.get('MYSQL_PORT')
name = env.get('MYSQL_DB')

engine_string = "mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8mb4" % (
    username, password, address, port, name)
engine = create_engine(engine_string, echo=False,
                       convert_unicode=True,
                       # close connections after 1h - as connections timeout at the database
                       pool_recycle=3600)

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
    bi = session.query(BulkInvoice).get(id)
    if bi is None:
        raise ResourceNotFound()
    return bi


def getBulkInvoiceList(session):
    return session.query(BulkInvoice).all()


def getInvoice(session, id):
    i = session.query(Invoice).get(id)
    if i is None:
        raise ResourceNotFound()
    return i


def getInvoiceWithESR(session, esr):
    i = session.query(Invoice).filter(Invoice.esr == esr).one()
    if i is None:
        raise ResourceNotFound()
    return i


def getInvoiceList(session, id):
    l = session.query(BulkInvoice).get(id).invoices
    if l is None:
        raise ResourceNotFound()
    return l

# Exceptions


class ResourceNotFound(Exception):
    ...
