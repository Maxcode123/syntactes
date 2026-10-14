from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Self

from syntactes.config import Symbol
from syntactes.parser.exception import LocationObjectError


@dataclass(frozen=True)
class Location:
    """
    Where a token starts in the source text. `offset` is 0-based, and `line`
    and `column` are 1-based.
    """

    offset: int
    line: int
    column: int

    @classmethod
    def from_object(cls, obj: Any) -> Self:
        """
        Builds a location from a mapping with the keys `offset`, `line` and
        `column`, or from any other object with those attributes, such as a
        lexer's own location. Other keys and attributes are ignored, and each
        value is converted with `int`.

        Raises `syntactes.parser.LocationObjectError` if a key or attribute is
        missing, or if its value can't be converted to an integer, with the
        conversion's exception as its cause.
        """
        attrs = ("offset", "line", "column")

        if isinstance(obj, Mapping):
            for key in attrs:
                if key not in obj:
                    raise LocationObjectError(
                        f"cannot create Location object from {obj!r}, missing {key!r} key"
                    )

            data = {}
            try:
                for key in attrs:
                    data[key] = int(obj.get(key))
            except (ValueError, TypeError) as e:
                raise LocationObjectError(
                    f"cannot create Location object from {obj!r}, {key!r} cannot be converted to an integer"
                ) from e

            return cls(**data)

        for attr in attrs:
            if not hasattr(obj, attr):
                raise LocationObjectError(
                    f"cannot create Location object from {obj!r}, missing attribute {attr!r}"
                )

        data = {}
        try:
            for attr in attrs:
                data[attr] = int(getattr(obj, attr))
        except (ValueError, TypeError) as e:
            raise LocationObjectError(
                f"cannot create Location object from {obj!r}, {attr!r} cannot be converted to an integer"
            ) from e

        return cls(**data)


class Token:
    """
    A token of the stream a parser reads: a terminal symbol, the `Location` it
    starts at, and the value it was read with, e.g.
    `Token(NUMBER, Location(0, 1, 1), "42")`. Callbacks receive one token per
    right-hand side symbol. A non-terminal's token holds the value computed for
    its rule, and the location of its first token (for an empty rule, of the
    token that follows it).

    Tokens are equal if their symbols and values are. Hashing uses only the
    symbol, so a token with an unhashable value can still be hashed.
    """

    def __init__(self, symbol: Symbol, location: Location, value: Any = None) -> None:
        self.symbol = symbol
        self.location = location
        self.value = value

    def __repr__(self) -> str:
        return f"<Token: {self.symbol}, {self.value!r}>"

    def __str__(self) -> str:
        return str(self.symbol)

    def __hash__(self) -> int:
        return hash(self.symbol)

    def __eq__(self, other) -> bool:
        if self is other:
            return True

        if not isinstance(other, Token):
            return False

        return self.symbol == other.symbol and self.value == other.value
