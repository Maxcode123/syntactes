from syntactes.token import Token


class Rule:
    """
    Production rule. Describes the break-down of a non-terminal symbol to
    other symbols.

    LHS -> RHS1 RHS2...
    """

    def __init__(self, number: int, lhs: Token, *rhs: Token) -> None:
        self.number = number
        self.lhs = lhs
        self.rhs = rhs
        self.rhs_len = len(rhs)

    def is_empty(self) -> bool:
        """
        Returns True if the rule derives the empty string directly, i.e. its
        right-hand side is empty or only ε.
        """
        null = Token.null()
        return all(s == null for s in self.rhs)

    def has_null_rhs(self) -> bool:
        """
        Same as `is_empty()`.
        """
        return self.is_empty()

    def __repr__(self) -> str:
        return f"<Rule: {self}>"

    def __str__(self) -> str:
        if self.is_empty():
            return f"{self.lhs} -> {Token.null()}"

        return f"{self.lhs} -> " + " ".join(map(str, self.rhs))

    def __hash__(self) -> int:
        return hash((self.lhs, self.rhs))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Rule):
            return False

        return self.lhs == other.lhs and self.rhs == other.rhs
