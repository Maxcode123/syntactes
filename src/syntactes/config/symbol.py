class Symbol:
    """
    A symbol of the grammar: a terminal or a non-terminal. Rules, grammars and
    parsing tables are made of symbols. The input of a parser is a stream of
    `Token`s, each holding the terminal symbol it was read as.
    """

    def __init__(self, name: str, is_terminal: bool) -> None:
        self.name = name
        self.is_terminal = is_terminal

    @staticmethod
    def null() -> "Symbol":
        """
        Returns the NULL symbol, ε.
        """
        return Symbol("ε", True)

    @staticmethod
    def eof() -> "Symbol":
        """
        Returns the EOF symbol, $.
        """
        return Symbol("$", True)

    def __repr__(self) -> str:
        return f"<Symbol: {self}>"

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if self is other:
            return True

        if not isinstance(other, Symbol):
            return False

        return self.name == other.name and self.is_terminal is other.is_terminal

    def __lt__(self, other) -> bool:
        if not isinstance(other, Symbol):
            raise ValueError(  # noqa: TRY004 (public behaviour; TypeError would break callers)
                f"'<' not supported between instances of 'Symbol' and {type(other).__name__}"
            )

        return self.name < other.name
