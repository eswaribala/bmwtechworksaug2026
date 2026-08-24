from typing import NamedTuple
from datetime import  date

class Car(NamedTuple):
    make: str
    model: str
    year: int
    color: str
    manufacture_date: date