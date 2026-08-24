
from fastapi import APIRouter

from vehiclemodule.dtos.vehicle_request import VehicleRequest
from vehiclemodule.dtos.vehicle_response import VehicleResponse
from vehiclemodule.services.vehicle_service_impl import VehicleServiceImpl


router = APIRouter(prefix="/vehicles/v1.0", tags=["vehicles"])

vehicleService = VehicleServiceImpl()

@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle_data: VehicleRequest) -> VehicleResponse:
    return vehicleService.create_vehicle(vehicle_data)

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int) -> VehicleResponse:
    return vehicleService.get_vehicle(vehicle_id)

@router.get("/", response_model=list[VehicleResponse])
def get_all_vehicles() -> list[VehicleResponse]:
    return vehicleService.get_all_vehicles()

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, vehicle_data: VehicleRequest) -> VehicleResponse:
    return vehicleService.update_vehicle(vehicle_id, vehicle_data)

@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int)->dict:
    result = vehicleService.delete_vehicle(vehicle_id)
    if result:
        return {"message": "Vehicle deleted successfully"}
    else:
        return {"message": "Vehicle not found"}
