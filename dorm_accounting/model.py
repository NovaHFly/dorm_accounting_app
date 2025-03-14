from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class RoomTypes(Enum):
    MALE = auto()
    FEMALE = auto()
    MIXED = auto()


class PersonGenders(Enum):
    MALE = auto()
    FEMALE = auto()


@dataclass
class Person:
    pk: int
    first_name: str
    last_name: str
    gender: PersonGenders
    age: int
    phone: str
    passport: str
    room: int
    father_name: Optional[str] = None


@dataclass
class Room:
    pk: int
    number: int
    kind: RoomTypes
    capacity: int

    @property
    def occupants(self) -> list:
        # Get list of occupants from database whose room number is equal to
        # self room number
        return NotImplemented

    @property
    def space(self) -> int:
        return self.capacity - len(self.occupants)
