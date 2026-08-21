from models.carconfig import car_frozen_set
from models.users import create_users
from models.projects import create_projects
from models.mapper import create_mapper
from models.coords import city_cords
from models.ipaddress import create_ipaddresses, set_operations
from faker import Faker
if __name__ == "__main__":    
    users = create_users()
    projects = create_projects()
    create_mapper(users, projects)
    #city cords
    print("City Coordinates:")
    cords = city_cords()
    print(cords)
    #count set of unique ip addresses
   
    ipaddresses = create_ipaddresses()
    print(f"Number of unique IP addresses generated: {len(ipaddresses)}")

    fake = Faker()
    #need bmw car models
    
    set1={"BMW X5", "BMW 3 Series", "BMW 5 Series", "BMW 7 Series", "BMW Z4"} 
    set2={"BMW X5", "BMW 3 Series", "BMW 5 Series", "BMW 7 Series", "BMW Z4", "BMW M3", "BMW M4", "BMW M5"}
    union_set, intersection_set, difference_set = set_operations(set1, set2)
    print(f"Union: {union_set}")
    print(f"Intersection: {intersection_set}")
    print(f"Difference: {difference_set}")
    #call the frozen set function from carconfig.py
    frozen_features = car_frozen_set()
    print(f"Frozen Features: {frozen_features}")