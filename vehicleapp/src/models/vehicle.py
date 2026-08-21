#create class Vehicle

"""Vehicle class representing a vehicle with VIN and model."""
class Vehicle:
    """Initialize a Vehicle instance with VIN and model.

        Args:
            vin (str): The Vehicle Identification Number.
            model (str): The model of the vehicle.
    """
    def __init__(self, vin, model):
        #protected attributes have double underscore prefix
        self._vin = vin
        self._model = model        

   
    #user friendly representation of the object
    """ String representation of the Vehicle instance.

        Returns:
            str: A string containing the VIN and model of the vehicle.
    """
    def __str__(self):
        return f"self._vin: {self._vin}, self._model: {self._model}, "
    #developers friendly representation of the object
    """ Developer-friendly representation of the Vehicle instance.

        Returns:
            str: A string containing the constructor call with VIN and model.
    """
    def __repr__(self):
        return f"Vehicle(vin={self._vin}, model={self._model})"