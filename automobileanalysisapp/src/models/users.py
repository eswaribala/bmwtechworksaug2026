#create 10 users in list
from faker import Faker
def create_users():
    users = []
    fake = Faker()
    for i in range(10):
        users.append(fake.name())
    return users