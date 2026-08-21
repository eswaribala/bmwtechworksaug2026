"""
Utility functions for creating vehicle objects.

This module creates ElectricVehicle or HybridVehicle objects
based on the supplied vehicle data.
"""

from models.vehicle import Vehicle
from models.hybrid_vehicle import HybridVehicle
from models.fuel_type import FuelType
from models.electric_vehicle import ElectricVehicle


def create_vehicle_object(vehicle_data):
    """
    Create a vehicle object based on the provided vehicle data.

    If ``fuel_type`` is None, an ElectricVehicle object is created.
    Otherwise, a HybridVehicle object is created.

    :param vehicle_data: Dictionary containing vehicle information.
    :type vehicle_data: dict
    :return: Created ElectricVehicle or HybridVehicle object.
    :rtype: Vehicle
    """

    # If fuel_type is None, create ElectricVehicle object
    if vehicle_data["fuel_type"] is None:
        vehicle_object = ElectricVehicle(
            vehicle_data["vin"],
            vehicle_data["model"],
            vehicle_data["battery_capacity"]
        )

    else:
        vehicle_object = HybridVehicle(
            vehicle_data["vin"],
            vehicle_data["model"],
            vehicle_data["fuel_type"],
            vehicle_data["battery_capacity"]
        )

    return vehicle_object


if __name__ == "__main__":
    # Test the create_vehicle_object function
    instance = create_vehicle_object({
        "vin": "1HGCM82633A004352",
        "model": "BMW i3",
        "fuel_type": FuelType.PETROL,
        "battery_capacity": 42
    })

    print(instance)
    print(repr(instance))