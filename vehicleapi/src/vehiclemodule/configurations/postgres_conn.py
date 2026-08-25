from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from vehiclemodule.configurations.config import Config

config = Config().get_database_connection_string()


base = declarative_base()

engine = create_async_engine(config,
                       echo=True,
                       pool_size=10,
                       max_overflow=20,
                       pool_timeout=30,
                       pool_recycle=1800)

sessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

class PGConnection:
    @staticmethod
    async def get_connection():
        return await engine.connect()

    @staticmethod
    def get_session():
        return sessionLocal()
    
  
    @staticmethod
    async def close_connection(conn):
        await conn.close()

    