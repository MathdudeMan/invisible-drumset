import enum

class side(enum.Enum):
    LEFT = 0
    RIGHT = 1

class extremity_type(enum.Enum):
    HAND = 0
    FOOT = 1

class state(enum.Enum):
    ON = 0
    OFF = 1
    OUT = 2
    