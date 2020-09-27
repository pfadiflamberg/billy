import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import BulkInvoice, Invoice
# Use the environment variables to create the engine string

username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PW')
address = os.getenv('POSTGRES_SERVER')
port = os.getenv('POSTGRES_PORT')
name = os.getenv('POSTGRES_DB')

engine_string = "postgresql+psycopg2://%s:%s@%s:%s/%s" % (username, password, address, port, name)
engine = create_engine(engine_string,echo=True)

# Create a sessionmaker
Session = sessionmaker(bind=engine)


from alembic.config import Config
from alembic import command
# Read the config
alembic_cfg = Config('alembic.ini')

# Load and return a session to the billy database

def loadSession():
    """"""    
    return Session()


# Functions to upgrade and downgrade to the specified version, if none specified: use head/base respectively

def upgradeDatabase(version="head"):
    # TODO: make independent of execution location, until then: upgrade via commandline
    command.upgrade(alembic_cfg, version)


def downgradeDatabase(version="base"):
    # TODO: make independent of execution location, until then: downgrade via commandline
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