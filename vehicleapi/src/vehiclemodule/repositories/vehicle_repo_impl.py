
from typing import List
from datetime import datetime

from vehiclemodule.configurations.postgres_conn import PGConnection
from vehiclemodule.dtos.vehicle_request import VehicleRequest
from vehiclemodule.exceptions.vehicledata_exception import VehicleDataException
from vehiclemodule.exceptions.vehicle_not_found_exception import VehicleNotFoundException
from vehiclemodule.repositories.vehicle_repository import VehicleRepository
from vehiclemodule.configurations.postgres_conn import PGConnection
from vehiclemodule.models.vehicle import Vehicle

class VehicleRepositoryImpl(VehicleRepository):

   def __init__(self):
        self.session=PGConnection().get_session()

   def get_vehicle_by_id(self, vehicle_id: int)-> Vehicle:
       # Implementation for retrieving a vehicle by its ID
       vehicle = self.session.query(Vehicle).filter_by(id=vehicle_id).first()
       if not vehicle:
           raise VehicleNotFoundException(f"Vehicle with ID {vehicle_id} not found.")
       return vehicle
   def get_all_vehicles(self)->List[Vehicle]:
       return self.session.query(Vehicle).all()

   def create_vehicle(self, vehicle_data:VehicleRequest)->Vehicle:
         newVehicle = Vehicle(
            make=vehicle_data.make,
            model=vehicle_data.model,
            year=vehicle_data.year,
            vin=vehicle_data.vin,
            created_at=datetime.now(),
         )
         try:
            self.session.add(newVehicle)
            self.session.commit()
         except:
            self.session.rollback()
            raise VehicleDataException("Error occurred while creating the vehicle.")
         return newVehicle
   def update_vehicle(self, vehicle_id: int, vehicle_data: VehicleRequest)-> Vehicle:
         existing_vehicle = self.session.query(Vehicle).filter_by(id=vehicle_id).first()
         if not existing_vehicle:
            raise VehicleNotFoundException(f"Vehicle with ID {vehicle_id} not found.")
         else:
            existing_vehicle.make = vehicle_data.make
            existing_vehicle.model = vehicle_data.model
            existing_vehicle.year = vehicle_data.year
            existing_vehicle.vin = vehicle_data.vin
            existing_vehicle.updated_at = datetime.now()
            try:
                self.session.commit()
            except:
                self.session.rollback()
                raise VehicleDataException("Error occurred while updating the vehicle.")
            return existing_vehicle

   def delete_vehicle(self, vehicle_id: int) -> bool:
        existing_vehicle = self.session.query(Vehicle).filter_by(id=vehicle_id).first()
        if not existing_vehicle:
            raise VehicleNotFoundException(f"Vehicle with ID {vehicle_id} not found.")
        try:
            self.session.delete(existing_vehicle)
            self.session.commit()
            return True
        except:
            self.session.rollback()
            raise VehicleDataException("Error occurred while deleting the vehicle.")
   