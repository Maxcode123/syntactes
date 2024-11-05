class Token:
    """
    A token of the grammar. Can be a terminal or non-terminal symbol.
    """

    def __init__(self, symbol: str, is_terminal: bool, value=None) -> None:
        self.symbol = symbol
        self.is_terminal = is_terminal
        self.value = value

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
