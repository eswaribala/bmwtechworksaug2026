from faker import Faker
def create_projects():
    projects = []
    fake = Faker()
    for i in range(10):
        projects.append(fake.company())
    return projects