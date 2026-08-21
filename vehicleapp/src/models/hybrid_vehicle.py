
from models.vehicle import Vehicle

"""HybridVehicle class representing a hybrid vehicle with VIN, model, fuel type, and battery capacity."""
class HybridVehicle(Vehicle):
    """Initialize a HybridVehicle instance with VIN, model, fuel type, and battery capacity.

        Args:
            vin (str): The Vehicle Identification Number.
            model (str): The model of the vehicle.
            fuel_type (str): The fuel type of the hybrid vehicle.
            battery_capacity (float): The battery capacity of the hybrid vehicle.
    """
    def __init__(self, vin, model, fuel_type, battery_capacity):
        super().__init__(vin, model)
        self.fuel_type = fuel_type
        self.battery_capacity = battery_capacity
    """String representation of the HybridVehicle instance.

        Returns:
            str: A string containing the VIN, model, fuel type, and battery capacity of the hybrid vehicle.
    """
    def __str__(self):
        return f"vin: {self.vin}, model: {self.model}, fuel_type: {self.fuel_type}, battery_capacity: {self.battery_capacity} kWh"
    """Developer-friendly representation of the HybridVehicle instance.

        Returns:
            str: A string containing the constructor call with VIN, model, fuel type, and battery capacity.
    """
    def __repr__(self):
        return f"HybridVehicle(vin={self.vin}, model={self.model}, fuel_type={self.fuel_type}, battery_capacity={self.battery_capacity})"
    