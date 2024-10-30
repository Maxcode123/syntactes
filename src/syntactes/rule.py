from syntactes.token import Token


class Rule:
    """
    Production rule. Describes the break-down of a non-terminal symbol to
    other symbols.

    LHS -> RHS1 RHS2...
    """

    def __init__(self, number: int, lhs: Token, *args: tuple[Token]) -> None:
        self.number = number
        self.lhs = lhs
        self.rhs = args
        self.rhs_len = len(args)

    def __repr__(self) -> str:
        return f"<Rule: {self}>"

    def __str__(self) -> str:
        return f"{self.lhs} -> " + " ".join(map(str, self.rhs))

    def __hash__(self) -> int:
        return hash((self.lhs, self.rhs))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Rule):
            return False

        return self.lhs == other.lhs and self.rhs == other.rhs
