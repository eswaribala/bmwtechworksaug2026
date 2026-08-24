from models.car import Car
from faker import Faker

if __name__ == "__main__":
    fake=Faker()
    #named tuple
    car = Car(
        make=fake.company(),
        model=fake.word(),
        year=fake.year(),
        color=fake.color_name(),
        manufacture_date=fake.date_this_century()
    )
    print(f"Car Details: {car}")