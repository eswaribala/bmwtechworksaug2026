
from abc import ABC

from vehiclemodule.dtos.vehicle_request import VehicleRequest
from vehiclemodule.models.vehicle import Vehicle
from typing import List

class VehicleRepository(ABC):

    def get_vehicle_by_id(self, vehicle_id: int) -> Vehicle:
        pass

    def get_all_vehicles(self) -> List[Vehicle]:
        pass

    def create_vehicle(self, vehicle_data:VehicleRequest) -> Vehicle:
        pass

    def update_vehicle(self, vehicle_id: int, vehicle_data: VehicleRequest) -> Vehicle:
        pass

    def delete_vehicle(self, vehicle_id: int) -> bool:
        pass