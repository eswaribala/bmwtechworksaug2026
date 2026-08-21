#create object for vehicle
from models.vehicle import Vehicle
from models.hybrid_vehicle import HybridVehicle
from models.fuel_type import FuelType
from models.electric_vehicle import ElectricVehicle

"""Create a vehicle object based on the provided vehicle data."""
def create_vehicle_object(vehicle_data):
  #if fuel_type is None, create ElectricVehicle object
  if vehicle_data['fuel_type'] is None:
    vehicle_object = ElectricVehicle(vehicle_data['vin'], 
                                      vehicle_data['model'],
                                      vehicle_data['battery_capacity']                                      )
  else:
   
    vehicle_object = HybridVehicle(vehicle_data['vin'], 
                                   vehicle_data['model'],
                                   vehicle_data['fuel_type'],
                                   vehicle_data['battery_capacity']
                                   )
    return vehicle_object

""" main function to test the create_vehicle_object function."""
if __name__ == "__main__":  
  instance= create_vehicle_object({
       'vin': '1HGCM82633A004352',
         'model': 'BMW i3',
         'fuel_type': FuelType.PETROL,
         'battery_capacity': 42
   })
  
  print(instance)
  print(repr(instance))