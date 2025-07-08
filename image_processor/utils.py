import enum
from typing import NamedTuple, Dict


# class Landmark(Dict):
#     x: float
#     y: float
#     vis: float


# Landmark = Dict[str, float]


class Side(enum.Enum):
    LEFT = 0
    RIGHT = 1


class ExtremityType(enum.Enum):
    HAND = 0
    FOOT = 1


class State(enum.Enum):
    ON = 0
    OFF = 1
    OUT = 2
