"""
Primitives a rule can be tagged with, as in `int % expr -> NUMBER`.

There are value types (`Integer`, `Float`, `String`, `NoneType`, `Boolean`),
whose call converts one value, and binary operations (`Addition`,
`EqualityComparison` and the rest), whose call takes two operands and
returns the result. Every primitive's `string()` is the name used in the
grammar text.
"""

from typing import Protocol, Self

_primitives = []

type Primitive = type[
    Integer
    | Float
    | String
    | NoneType
    | Boolean
    | Addition
    | Subtraction
    | Multiplication
    | Division
    | Exponentiation
    | LowerThanComparison
    | LowerEqualThanComparison
    | GreaterThanComparison
    | GreaterEqualThanComparison
    | EqualityComparison
    | InequalityComparison
]


def primitives() -> tuple[Primitive, ...]:
    """
    Every primitive, in the order they're defined in this module.
    """
    return tuple(_primitives)


def _primitive(cls: type[Primitive]) -> type[Primitive]:
    _primitives.append(cls)
    return cls


class _Number(Protocol):
    def __add__(self, other: Self, /) -> Self: ...
    def __sub__(self, other: Self, /) -> Self: ...
    def __mul__(self, other: Self, /) -> Self: ...
    def __truediv__(self, other: Self, /) -> float: ...
    def __pow__(self, other: Self, /) -> Self: ...
    def __lt__(self, other: Self, /) -> bool: ...
    def __le__(self, other: Self, /) -> bool: ...
    def __gt__(self, other: Self, /) -> bool: ...
    def __ge__(self, other: Self, /) -> bool: ...


@_primitive
class Integer:
    """
    The `int` primitive. `Integer(value)` returns `int(value)`.
    """

    def __new__(cls, val: str) -> int:
        return int(val)

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "int"


@_primitive
class Float:
    """
    The `float` primitive. `Float(value)` returns `float(value)`.
    """

    def __new__(cls, val: str) -> float:
        return float(val)

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "float"


@_primitive
class String:
    """
    The `str` primitive. `String(value)` returns `str(value)`.
    """

    def __new__(cls, val: str) -> str:
        return str(val)

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "str"


@_primitive
class NoneType:
    """
    The `None` primitive. `NoneType(value)` always returns `None`.
    """

    def __new__(cls, val: str) -> None:
        return None

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "None"


@_primitive
class Boolean:
    """
    The `bool` primitive. `Boolean(value)` returns `True` if `value` is
    `"1"` or `"true"`, and `False` otherwise.
    """

    def __new__(cls, val: str) -> bool:
        return val in {"1", "true"}

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "bool"


@_primitive
class Addition[T: _Number]:
    """
    The `add` primitive. `Addition(left, right)` returns `left + right`.
    """

    def __new__(cls, left: T, right: T) -> T:
        return left + right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "add"


@_primitive
class Subtraction[T: _Number]:
    """
    The `sub` primitive. `Subtraction(left, right)` returns `left - right`.
    """

    def __new__(cls, left: T, right: T) -> T:
        return left - right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "sub"


@_primitive
class Multiplication[T: _Number]:
    """
    The `mul` primitive. `Multiplication(left, right)` returns `left * right`.
    """

    def __new__(cls, left: T, right: T) -> T:
        return left * right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "mul"


@_primitive
class Division[T: _Number]:
    """
    The `div` primitive. `Division(left, right)` returns `left / right`.
    """

    def __new__(cls, left: T, right: T) -> float:
        return left / right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "div"


@_primitive
class Exponentiation[T: _Number]:
    """
    The `pow` primitive. `Exponentiation(left, right)` returns
    `left ** right`.
    """

    def __new__(cls, left: T, right: T) -> T:
        return left**right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "pow"


@_primitive
class LowerThanComparison[T: _Number]:
    """
    The `lt` primitive. `LowerThanComparison(left, right)` returns
    `left < right`.
    """

    def __new__(cls, left: T, right: T) -> bool:
        return left < right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "lt"


@_primitive
class LowerEqualThanComparison[T: _Number]:
    """
    The `le` primitive. `LowerEqualThanComparison(left, right)` returns
    `left <= right`.
    """

    def __new__(cls, left: T, right: T) -> bool:
        return left <= right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "le"


@_primitive
class GreaterThanComparison[T: _Number]:
    """
    The `gt` primitive. `GreaterThanComparison(left, right)` returns
    `left > right`.
    """

    def __new__(cls, left: T, right: T) -> bool:
        return left > right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "gt"


@_primitive
class GreaterEqualThanComparison[T: _Number]:
    """
    The `ge` primitive. `GreaterEqualThanComparison(left, right)` returns
    `left >= right`.
    """

    def __new__(cls, left: T, right: T) -> bool:
        return left >= right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "ge"


@_primitive
class EqualityComparison[T]:
    """
    The `eq` primitive. `EqualityComparison(left, right)` returns
    `left == right`.
    """

    def __new__(cls, left: T, right: T) -> bool:
        return left == right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "eq"


@_primitive
class InequalityComparison[T]:
    """
    The `ne` primitive. `InequalityComparison(left, right)` returns
    `left != right`.
    """

    def __new__(cls, left: T, right: T) -> bool:
        return left != right

    @classmethod
    def string(cls) -> str:
        """
        Returns the primitive's name in the grammar text.
        """
        return "ne"
