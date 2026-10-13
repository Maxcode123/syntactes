from typing import Any

from syntactes.config import Symbol


class Token:
    """
    A token of the stream a parser reads: a terminal symbol and the value it was
    read with, e.g. `Token(NUMBER, "42")`. Callbacks receive one token per
    right-hand side symbol, and a non-terminal's token holds the value computed
    for its rule.

    Tokens are equal if their symbols and values are. Hashing uses only the
    symbol, so a token with an unhashable value can still be hashed.
    """

    def __init__(self, symbol: Symbol, value: Any = None) -> None:
        self.symbol = symbol
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
