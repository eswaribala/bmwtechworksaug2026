#create object for vehicle
from models.vehicle import Vehicle

def create_vehicle_object(vehicle_data):
    vehicle_object = Vehicle(vehicle_data['vin'], 
                             vehicle_data['model']
                             )
    return vehicle_object

if __name__ == "__main__":  
  instance= create_vehicle_object({
       'vin': '1HGCM82633A004352',
         'model': 'BMW i3'
   })
  
  print(instance)
  print(repr(instance))