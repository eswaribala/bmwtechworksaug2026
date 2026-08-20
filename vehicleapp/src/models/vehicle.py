#create class Vehicle
class Vehicle:
    def __init__(self, vin, model, battery_kwh):
        #private attributes have double underscore prefix
        self.__vin = vin
        self.__model = model
        if not self.validate_battery_kwh():
            raise ValueError("Battery capacity cannot be negative.")
        self.__battery_kwh = battery_kwh

    #getter methods for private attributes
    @property
    def battery_kwh(self):
        return self.__battery_kwh

    @battery_kwh.setter
    def battery_kwh(self, value):
        if not self.validate_battery_kwh():
            raise ValueError("Battery capacity cannot be negative.")
        self.__battery_kwh = value

    def validate_battery_kwh(self):
        if self.__battery_kwh < 0:
            return False
        return True

    #user friendly representation of the object
    def __str__(self):
        return f"self.__vin: {self.__vin}, self.__model: {self.__model}, self.__battery_kwh: {self.__battery_kwh}"
    #developers friendly representation of the object
    def __repr__(self):
        return f"Vehicle(vin={self.__vin}, model={self.__model}, battery_kwh={self.__battery_kwh})"