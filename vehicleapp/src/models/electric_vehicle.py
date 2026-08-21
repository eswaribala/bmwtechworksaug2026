from models.electric_system import ElectricSystem
from models.vehicle import Vehicle
"""ElectricVehicle class representing an electric vehicle with VIN, model, and battery capacity."""
class ElectricVehicle(ElectricSystem,Vehicle):
    """Initialize an ElectricVehicle instance with VIN, model, and battery capacity.

        Args:
            vin (str): The Vehicle Identification Number.
            model (str): The model of the vehicle.
            battery_capacity (float): The battery capacity of the electric vehicle.
    """
    def __init__(self, vin, model, battery_capacity, voltage=0, current=0,adas_system=None):
        ElectricSystem.__init__(self, voltage=voltage, current=current)  # Initialize ElectricSystem with provided values
        Vehicle.__init__(self, vin, model, adas_system=adas_system)
        self.validate_battery_capacity(battery_capacity)
        self.__battery_capacity = battery_capacity
    """Battery capacity of the electric vehicle."""
    @property
    def battery_capacity(self):
        return self.__battery_capacity
    """Set the battery capacity of the electric vehicle.

        Args:
            battery_capacity (float): The new battery capacity of the electric vehicle.
        """
    @battery_capacity.setter 
    def battery_capacity(self, battery_capacity):
        self.validate_battery_capacity(battery_capacity)
        self.__battery_capacity = battery_capacity
    """Validate the battery capacity to ensure it is a positive value.

        Args:
            battery_capacity (float): The battery capacity to validate.
        Raises:
            ValueError: If the battery capacity is not a positive value.
    """

    def validate_battery_capacity(self, battery_capacity):
        if battery_capacity <= 0:
            raise ValueError("Battery capacity must be a positive value.")
    """String representation of the ElectricVehicle instance.

        Returns:
            str: A string containing the VIN, model, and battery capacity of the electric vehicle.
    """
    def __str__(self):
      
        return f"{super().__str__()}, self.__battery_capacity: {self.__battery_capacity}"

    """Developer-friendly representation of the ElectricVehicle instance.

        Returns:
            str: A string containing the constructor call with VIN, model, and battery capacity.
    """
    def __repr__(self):
        return f"ElectricVehicle(vin={self._vin}, model={self._model}, battery_capacity={self.__battery_capacity})"
   