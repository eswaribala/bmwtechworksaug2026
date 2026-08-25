
from abc import ABC, abstractmethod
from vehiclemodule.dtos.vehicle_response import VehicleResponse
from typing import List
from vehiclemodule.dtos.vehicle_request import VehicleRequest

class VehicleService(ABC):
    @abstractmethod
    async def get_all_vehicles(self) -> List[VehicleResponse]:
        pass
    @abstractmethod
    async def get_vehicle_by_id(self, vehicle_id: int) -> VehicleResponse:
        pass
    @abstractmethod
    async def create_vehicle(self, vehicle_data: VehicleRequest) -> VehicleResponse:
        pass
    @abstractmethod
    async def update_vehicle(self, vehicle_id: int, vehicle_data: VehicleRequest) -> VehicleResponse:
        pass
    @abstractmethod
    async def delete_vehicle(self, vehicle_id: int) -> bool:
        pass