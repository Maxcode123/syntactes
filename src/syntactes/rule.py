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
        # Rules are hashed and checked for emptiness constantly while generating
        # tables, so both are computed once.
        null = Token.null()
        self._is_empty = all(s == null for s in rhs)
        self._hash = hash((lhs, rhs))

    def is_empty(self) -> bool:
        """
        Returns True if the rule derives the empty string directly, i.e. its
        right-hand side is empty or only ε.
        """
        return self._is_empty

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
        return self._hash

    def __eq__(self, other) -> bool:
        if self is other:
            return True

        if not isinstance(other, Rule):
            return False

        return self.lhs == other.lhs and self.rhs == other.rhs
