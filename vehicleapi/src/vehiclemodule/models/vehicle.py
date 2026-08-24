from vehiclemodule.configurations.postgres_conn import base
from sqlalchemy import Column,DateTime,Integer,String
class Vehicle(base):
    __tablename__ = 'vehicle'
    id = Column(Integer, primary_key=True, autoincrement=True)
    make =Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    vin = Column(String(17), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Vehicle(id={self.id}, make='{self.make}', model='{self.model}', year={self.year}, vin='{self.vin}', created_at='{self.created_at}', updated_at='{self.updated_at}')>"