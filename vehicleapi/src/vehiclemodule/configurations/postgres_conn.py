from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from vehiclemodule.configurations.config import Config

config = Config().get_database_connection_string()

from sqlalchemy.ext.declarative import declarative_base
base = declarative_base()

engine = create_engine(config,
                       echo=True,
                       pool_size=10,
                       max_overflow=20,
                       pool_timeout=30,
                       pool_recycle=1800)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class PGConnection:
    @staticmethod
    def get_connection():
        return engine.connect()

    @staticmethod
    def get_session():
        return sessionLocal()
    
    @staticmethod
    def close_connection(conn):
        conn.close()

    