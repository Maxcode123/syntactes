from typing import Optional

from syntactes.rule import Rule
from syntactes.token import Token


class LR0Item:
    """
    Item of LR0 parser. Contains rule and current position in rule.
    Current position is denoted with the dot '.'.
    """

    def __init__(self, rule: Rule, position: int) -> None:
        self.rule = rule
        self.position = position

    def dot_is_last(self) -> bool:
        """
        Returns True if the dot in the item is in the last position of the rhs,
        False otherwise.
        """
        return self.position == self.rule.rhs_len

    @property
    def after_dot(self) -> Optional[Token]:
        """
        Returns the symbol after the dot in the current item.
        If the dot is in the last position, returns None
        """
        if self.dot_is_last():
            return None

        return self.rule.rhs[self.position]

    @property
    def before_dot(self) -> Optional[Token]:
        """
        Returns the symbol before the dot in the current item.
        If the dot is in the first position, returns None.
        """
        if self.position == 0:
            return None

        return self.rule.rhs[self.position - 1]

    def __repr__(self) -> str:
        return f"<LR0Item: {self}>"

    def __str__(self) -> str:
        rhs = [s for s in self.rule.rhs]
        rhs.insert(self.position, ".")
        return f"{self.rule.lhs} -> " + " ".join(map(str, rhs))

    def __hash__(self) -> int:
        return hash((self.rule, self.position))

    def __eq__(self, other) -> bool:
        if not isinstance(other, LR0Item):
            return False

        return self.rule == other.rule and self.position == other.position
