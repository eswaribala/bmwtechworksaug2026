from typing import List
from datetime import datetime

from sqlalchemy import select

from vehiclemodule.configurations.postgres_conn import PGConnection
from vehiclemodule.dtos.vehicle_request import VehicleRequest
from vehiclemodule.exceptions.vehicledata_exception import VehicleDataException
from vehiclemodule.exceptions.vehicle_not_found_exception import (
    VehicleNotFoundException,
)
from vehiclemodule.repositories.vehicle_repository import VehicleRepository
from vehiclemodule.models.vehicle import Vehicle


class VehicleRepositoryImpl(VehicleRepository):

    def __init__(self):
        self.session = PGConnection.get_session()

    async def get_vehicle_by_id(
        self,
        vehicle_id: int
    ) -> Vehicle:

        stmt = select(Vehicle).where(
            Vehicle.id == vehicle_id
        )

        result = await self.session.execute(stmt)

        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise VehicleNotFoundException(
                f"Vehicle with ID {vehicle_id} not found."
            )

        return vehicle

    async def get_all_vehicles(
        self
    ) -> List[Vehicle]:

        stmt = select(Vehicle)

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def create_vehicle(
        self,
        vehicle_data: VehicleRequest
    ) -> Vehicle:

        new_vehicle = Vehicle(
            make=vehicle_data.make,
            model=vehicle_data.model,
            year=vehicle_data.year,
            vin=vehicle_data.vin,
            created_at=datetime.now(),
        )

        try:
            self.session.add(new_vehicle)

            await self.session.commit()

            await self.session.refresh(new_vehicle)

            return new_vehicle

        except Exception as exc:

            await self.session.rollback()

            raise VehicleDataException(
                "Error occurred while creating the vehicle."
            ) from exc

    async def update_vehicle(
        self,
        vehicle_id: int,
        vehicle_data: VehicleRequest
    ) -> Vehicle:

        existing_vehicle = await self.get_vehicle_by_id(
            vehicle_id
        )

        existing_vehicle.make = vehicle_data.make
        existing_vehicle.model = vehicle_data.model
        existing_vehicle.year = vehicle_data.year
        existing_vehicle.vin = vehicle_data.vin
        existing_vehicle.updated_at = datetime.now()

        try:

            await self.session.commit()

            await self.session.refresh(existing_vehicle)

            return existing_vehicle

        except Exception as exc:

            await self.session.rollback()

            raise VehicleDataException(
                "Error occurred while updating the vehicle."
            ) from exc

    async def delete_vehicle(
        self,
        vehicle_id: int
    ) -> bool:

        existing_vehicle = await self.get_vehicle_by_id(
            vehicle_id
        )

        try:

            await self.session.delete(existing_vehicle)

            await self.session.commit()

            return True

        except Exception as exc:

            await self.session.rollback()

            raise VehicleDataException(
                "Error occurred while deleting the vehicle."
            ) from exc