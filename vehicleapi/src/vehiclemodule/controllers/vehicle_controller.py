from fastapi import APIRouter

from vehiclemodule.dtos.vehicle_request import VehicleRequest
from vehiclemodule.dtos.vehicle_response import VehicleResponse
from vehiclemodule.services.vehicle_service_impl import VehicleServiceImpl


router = APIRouter(
    prefix="/vehicles/v1.0",
    tags=["vehicles"]
)

vehicleService = VehicleServiceImpl()


@router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    vehicle_data: VehicleRequest
) -> VehicleResponse:

    return await vehicleService.create_vehicle(
        vehicle_data
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int
) -> VehicleResponse:

    return await vehicleService.get_vehicle_by_id(
        vehicle_id
    )


@router.get("/", response_model=list[VehicleResponse])
async def get_all_vehicles() -> list[VehicleResponse]:

    return await vehicleService.get_all_vehicles()


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleRequest
) -> VehicleResponse:

    return await vehicleService.update_vehicle(
        vehicle_id,
        vehicle_data
    )


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int
) -> dict:

    result = await vehicleService.delete_vehicle(
        vehicle_id
    )

    if result:
        return {
            "message": "Vehicle deleted successfully"
        }

    return {
        "message": "Vehicle not found"
    }