from faker import Faker
def create_ipaddresses():
    fake = Faker()
    ipaddresses = []
    for i in range(1000000):
        ip = fake.ipv4()
        ipaddresses.append(ip)
    return set(ipaddresses)

def set_operations(set1, set2):
    #union
    union_set = set1 | set2
    #intersection
    intersection_set = set1 & set2
    #difference
    difference_set = set1 - set2
    return union_set, intersection_set, difference_set