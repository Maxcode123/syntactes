from typing import Any


class Integer:
    def __new__(cls, val: Any) -> int:
        return int(val)

    @classmethod
    def string(cls) -> str:
        return "int"


class Float:
    def __new__(cls, val: Any) -> float:
        return float(val)

    @classmethod
    def string(cls) -> str:
        return "float"


class String:
    def __new__(cls, val: Any) -> str:
        return str(val)

    @classmethod
    def string(cls) -> str:
        return "str"


class NoneType:
    def __new__(cls, val: Any) -> None:
        return None

    @classmethod
    def string(cls) -> str:
        return "None"


type Primitive = type[Integer | Float | String | NoneType]
