#create object for vehicle
from models.vehicle import Vehicle

def create_vehicle_object(vehicle_data):
    vehicle_object = Vehicle(vehicle_data['vin'], 
                             vehicle_data['model'], 
                             vehicle_data['battery_kwh'])
    return vehicle_object

if __name__ == "__main__":  
   create_vehicle_object({
       'vin': '1HGCM82633A004352',
         'model': 'BMW i3',
         'battery_kwh': 87.5
   })