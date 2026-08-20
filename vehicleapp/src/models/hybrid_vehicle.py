
from models.vehicle import Vehicle


class HybridVehicle(Vehicle):
    def __init__(self, vin, model, fuel_type, battery_capacity):
        super().__init__(vin, model)
        self.fuel_type = fuel_type
        self.battery_capacity = battery_capacity

    def __str__(self):
        return f"vin: {self.vin}, model: {self.model}, fuel_type: {self.fuel_type}, battery_capacity: {self.battery_capacity} kWh"

    def __repr__(self):
        return f"HybridVehicle(vin={self.vin}, model={self.model}, fuel_type={self.fuel_type}, battery_capacity={self.battery_capacity})"
    