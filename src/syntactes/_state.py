from collections.abc import Iterable
from typing import Protocol, Self

from syntactes._item import LR0Item, LR1Item


class State(Protocol):
    number: int | None
    is_final: bool

    def set_number(self, number: int) -> None: ...

    def set_final(self) -> None: ...


class LR0State:
    """
    State of LR0 parser. A LR0 state is a set of LR0 items.
    """

    def __init__(self) -> None:
        self.number: int | None = None
        self.items: set[LR0Item] = set()
        self.is_final = False

    @classmethod
    def from_items(cls, items: Iterable[LR0Item]) -> Self:
        """
        Create a state from a set of items.
        """
        state = cls()
        for item in items:
            state.add_item(item)

        return state

    def add_item(self, item: LR0Item) -> None:
        """
        Adds an item to the state.
        """
        self.items.add(item)

    def set_number(self, number: int) -> None:
        self.number = number

    def set_final(self) -> None:
        self.is_final = True

    def __repr__(self) -> str:
        return f"<LR0State: {self.number}>"

    def __str__(self) -> str:
        return f"{self.number}:" + "(" + ", ".join(map(str, self.items)) + ")"

    def __hash__(self) -> int:
        return hash(frozenset(self.items))

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.items == other.items


class LR1State(LR0State):
    """
    State of LR1 parser. An LR1 state is a set of LR1 items.
    """

    items: set[LR1Item]

    def __repr__(self) -> str:
        return f"<LR1State: {self.number}>"
