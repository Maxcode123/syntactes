from enum import Enum
from typing import Any, Optional


class OperatorType(Enum):
    """
    A token can be an operator, operating on other tokens; this enum defines the
    associativity of an operator; that is, it determines how certain expressions
    get parsed.

    e.g.
    x 'op' y 'op' z can be interpreted as (x 'op' y) 'op' z or x 'op' (y 'op' z)
    where 'op' is a binary operator.
    A binary left associative operator results in the former whereas a binary
    right associative operator in the latter.

    Furthermore, unary operators can associate to the token immediately after
    or before.

    e.g.
    x 'op' y can be interpreted as (x 'op') y or x ('op' y)
    where 'op' is a unary operator.
    A unary post-associative operator results in the former whereas a unary
    pre-associative operator results in the latter.
    """

    BINARY_LEFT_ASSOCIATIVE = "BINARY_LEFT_ASSOCIATIVE"
    BINARY_RIGHT_ASSOCIATIVE = "BINARY_RIGHT_ASSOCIATIVE"
    UNARY_POST_ASSOCIATIVE = "UNARY_POST_ASSOCIATIVE"
    UNARY_PRE_ASSOCIATIVE = "UNARY_PRE_ASSOCIATIVE"


class Token:
    """
    A token of the grammar. Can be a terminal or non-terminal symbol.
    """

    def __init__(
        self,
        symbol: str,
        is_terminal: bool,
        *,
        operator_type: Optional[OperatorType] = None,
        value: Any = None,
    ) -> None:
        self.symbol = symbol
        self.is_terminal = is_terminal
        self.operator_type = operator_type
        self.value = value

    @staticmethod
    def operator(symbol: str, operator_type: OperatorType) -> "Token":
        """
        Shorthand method to create an operator.
        """
        return Token(symbol, True, operator_type=operator_type)

    @staticmethod
    def null() -> "Token":
        """
        Returns the NULL token.
        """
        return Token("ε", True)

    @staticmethod
    def eof() -> "Token":
        """
        Returns the EOF token.
        """
        return Token("$", True)

    def __repr__(self) -> str:
        return f"<Token: {self}>"

    def __str__(self) -> str:
        return self.symbol

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Token):
            return False

        return self.symbol == other.symbol and self.is_terminal is other.is_terminal

    def __lt__(self, other) -> bool:
        if not isinstance(other, Token):
            raise ValueError(
                f"'<' not supported between instances of 'Token' and {type(other).__name__}"
            )

        return self.symbol < other.symbol
