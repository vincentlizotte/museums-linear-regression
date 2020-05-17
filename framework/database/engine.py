from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from resources.configs import config


engine = create_engine(config.database_connection_string, echo=config.database_echo)
connection = engine.connect()

ModelBase = declarative_base()
ModelBase.metadata.bind = engine

SessionFactory = sessionmaker(bind=engine)

