#create class Vehicle
class Vehicle:
    def __init__(self, vin, model, battery_kwh):
        #private attributes have double underscore prefix
        self.__vin = vin
        self.__model = model
        self.__battery_kwh = battery_kwh
    #user friendly representation of the object
    def __str__(self):
        return f"self.__vin: {self.__vin}, self.__model: {self.__model}, self.__battery_kwh: {self.__battery_kwh}"
    #developers friendly representation of the object
    def __repr__(self):
        return f"Vehicle(vin={self.__vin}, model={self.__model}, battery_kwh={self.__battery_kwh})"