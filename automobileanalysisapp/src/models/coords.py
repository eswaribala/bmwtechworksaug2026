from faker import Faker

def city_cords():
    fake = Faker()
    cities = []    
    for i in range(10):
        cords = (fake.latitude(), fake.longitude())
        cities.append(cords)
    #convert list to tuple
    return tuple(cities)

    
