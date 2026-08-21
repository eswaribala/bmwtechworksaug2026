
from models.ipaddress import set_operations


def car_frozen_set():
    frozen_features = frozenset({"Sunroof", "Leather Seats", "Bluetooth", "Backup Camera", "Navigation System"})
    #frozen_features.add("Heated Seats")  # This will raise an AttributeError since frozenset is immutable
    return frozen_features

def car_frozen_set_list():
    config_list=[]
    frozen_features1 = frozenset({"Sunroof", "Leather Seats", "Bluetooth", "Backup Camera", "Navigation System"})
    config_list.append(frozen_features1)
    frozen_features2 = frozenset({"Heated Seats", "All-Wheel Drive", "Remote Start"})
    config_list.append(frozen_features2)
    return config_list

def car_prize():
    price_dict = {}
    #create a dictionary with car models and their prices
    for frozen_data in car_frozen_set_list():
        price_dict[frozen_data] = 20000 + (len(frozen_data) * 5000)  # Example pricing logic based on number of features
    return price_dict
        