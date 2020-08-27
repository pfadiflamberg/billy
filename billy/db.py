from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import model

from alembic.config import Config
from alembic import command


engine_string = "postgresql+psycopg2://postgres:password@billy-postgres:5432/billy"
engine = create_engine(engine_string,echo=True)
Base = declarative_base(engine)


# Load and return a session to the billy database

def loadSession():
    """"""    
    meta = MetaData(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


# Functions to upgrade and downgrade to the specified version, if none specified: use head/base respectively

def upgradeDatabase(version="head"):
    # TODO: make independent of execution location, until then: upgrade via commandline
    alembic_cfg = Config('alembic.ini')

    command.upgrade(alembic_cfg, version)


def downgradeDatabase(version="base"):
    # TODO: make independent of execution location, until then: downgrade via commandline
    alembic_cfg = Config('alembic.ini')

    command.downgrade(alembic_cfg, version)