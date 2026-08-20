from models.vehicle import Vehicle
class ElectricVehicle(Vehicle):
    def __init__(self, vin, model, battery_capacity):
        super().__init__(vin, model)
        self.validate_battery_capacity(battery_capacity)
        self.__battery_capacity = battery_capacity
    @property
    def battery_capacity(self):
        return self.__battery_capacity
    @battery_capacity.setter 
    def battery_capacity(self, battery_capacity):
        self.validate_battery_capacity(battery_capacity)
        self.__battery_capacity = battery_capacity

    def validate_battery_capacity(self, battery_capacity):
        if battery_capacity <= 0:
            raise ValueError("Battery capacity must be a positive value.")

    def __str__(self):
        return f"self._vin: {self._vin}, self._model: {self._model}, self.__battery_capacity: {self.__battery_capacity}"

    def __repr__(self):
        return f"ElectricVehicle(vin={self._vin}, model={self._model}, battery_capacity={self.__battery_capacity})"
   