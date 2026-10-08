"""
Primitive types a rule can be tagged with, as in `int % expr -> NUMBER`.

Calling a primitive converts a value to its type, and its `string()` is the
name used in the grammar text.
"""

from typing import Any


class Integer:
    """
    The `int` primitive. `Integer(value)` returns `int(value)`.
    """

    def __new__(cls, val: Any) -> int:
        return int(val)

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "int"


class Float:
    """
    The `float` primitive. `Float(value)` returns `float(value)`.
    """

    def __new__(cls, val: Any) -> float:
        return float(val)

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "float"


class String:
    """
    The `str` primitive. `String(value)` returns `str(value)`.
    """

    def __new__(cls, val: Any) -> str:
        return str(val)

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "str"


class NoneType:
    """
    The `None` primitive. `NoneType(value)` always returns `None`.
    """

    def __new__(cls, val: Any) -> None:
        return None

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "None"


type Primitive = type[Integer | Float | String | NoneType]
