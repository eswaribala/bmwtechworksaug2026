

from vehiclemodule.dtos.vehicle_response import VehicleResponse
from vehiclemodule.repositories.vehicle_repo_impl import VehicleRepositoryImpl
from vehiclemodule.services.vehicle_service import VehicleService
from vehiclemodule.models.vehicle import Vehicle
from vehiclemodule.dtos.vehicle_request import VehicleRequest
from vehiclemodule.dtos.vehicle_response import VehicleResponse

class VehicleServiceImpl(VehicleService):
    def __init__(self):
        self.vehicle_repository = VehicleRepositoryImpl()

    def create_vehicle(self, vehicle_request: VehicleRequest) -> VehicleResponse:

        vehicle = self.vehicle_repository.create_vehicle(vehicle_request)
        if vehicle:
            return VehicleResponse(
                id=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                vin=vehicle.vin,
                created_at=vehicle.created_at,
                updated_at=vehicle.updated_at
            )
        return None

    def get_vehicle_by_id(self, vehicle_id: int) -> VehicleResponse:
        vehicle = self.vehicle_repository.get_vehicle_by_id(vehicle_id)
        if vehicle:
            return VehicleResponse(
                id=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                vin=vehicle.vin,
                created_at=vehicle.created_at,
                updated_at=vehicle.updated_at
            )
        return None

    def update_vehicle(self, vehicle_id: int, vehicle_request: VehicleRequest) -> VehicleResponse:
        vehicle = self.vehicle_repository.update_vehicle(vehicle_id, vehicle_request)
        if vehicle:
            return VehicleResponse(
                id=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                vin=vehicle.vin,
                created_at=vehicle.created_at,
                updated_at=vehicle.updated_at
            )
        return None

    def delete_vehicle(self, vehicle_id: int) -> bool:
        return self.vehicle_repository.delete_vehicle(vehicle_id)

    def get_all_vehicles(self) -> list[VehicleResponse]:
        vehicles = self.vehicle_repository.get_all_vehicles()
        return [
            VehicleResponse(
                id=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                vin=vehicle.vin,
                created_at=vehicle.created_at,
                updated_at=vehicle.updated_at
            ) for vehicle in vehicles
        ]

    