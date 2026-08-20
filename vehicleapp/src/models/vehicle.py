#create class Vehicle
class Vehicle:
    def __init__(self, vin, model):
        #protected attributes have double underscore prefix
        self._vin = vin
        self._model = model        

   
    #user friendly representation of the object
    def __str__(self):
        return f"self._vin: {self._vin}, self._model: {self._model}, "
    #developers friendly representation of the object
    def __repr__(self):
        return f"Vehicle(vin={self._vin}, model={self._model})"