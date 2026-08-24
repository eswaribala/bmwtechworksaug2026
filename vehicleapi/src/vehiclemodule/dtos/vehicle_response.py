from pydantic import BaseModel


class VehicleResponse(BaseModel):
    """
    VehicleResponse is a Pydantic model that represents the response for vehicle information.
    It includes the following fields:
    - id: An integer representing the unique identifier of the vehicle.
    - make: A string representing the manufacturer of the vehicle.
    - model: A string representing the model of the vehicle.
    - year: An integer representing the year of manufacture of the vehicle.
    - vin: A string representing the Vehicle Identification Number (VIN).
    - created_at: A string representing the creation timestamp of the vehicle record.
    - updated_at: A string representing the last update timestamp of the vehicle record.
    """

    id: int 
    make: str 
    model: str 
    year: int 
    vin: str  
    created_at: str
    updated_at: str 