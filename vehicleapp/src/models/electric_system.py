class ElectricSystem:
    def __init__(self, voltage, current):
        self.__voltage = voltage
        self.__current = current

    def power(self):
        return f"Electric system is powered on with voltage {self.__voltage}V and current {self.__current}A."