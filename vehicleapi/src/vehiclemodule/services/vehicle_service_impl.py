from vehiclemodule.dtos.vehicle_request import VehicleRequest
from vehiclemodule.dtos.vehicle_response import VehicleResponse
from vehiclemodule.repositories.vehicle_repo_impl import VehicleRepositoryImpl
from vehiclemodule.services.vehicle_service import VehicleService


class VehicleServiceImpl(VehicleService):

    def __init__(self):
        self.vehicle_repository = VehicleRepositoryImpl()

    async def create_vehicle(
        self,
        vehicle_request: VehicleRequest
    ) -> VehicleResponse | None:

        vehicle = await self.vehicle_repository.create_vehicle(
            vehicle_request
        )

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

    async def get_vehicle_by_id(
        self,
        vehicle_id: int
    ) -> VehicleResponse | None:

        vehicle = await self.vehicle_repository.get_vehicle_by_id(
            vehicle_id
        )

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

    async def update_vehicle(
        self,
        vehicle_id: int,
        vehicle_request: VehicleRequest
    ) -> VehicleResponse | None:

        vehicle = await self.vehicle_repository.update_vehicle(
            vehicle_id,
            vehicle_request
        )

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

    async def delete_vehicle(
        self,
        vehicle_id: int
    ) -> bool:

        return await self.vehicle_repository.delete_vehicle(
            vehicle_id
        )

    async def get_all_vehicles(
        self
    ) -> list[VehicleResponse]:

        vehicles = await self.vehicle_repository.get_all_vehicles()

        return [
            VehicleResponse(
                id=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                vin=vehicle.vin,
                created_at=vehicle.created_at,
                updated_at=vehicle.updated_at
            )
            for vehicle in vehicles
        ]