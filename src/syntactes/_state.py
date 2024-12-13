from typing import Iterable, Optional, Protocol

from syntactes._item import Item, LR0Item, LR1Item


class State(Protocol):
    number: Optional[int]
    items: set[Item]


class LR0State:
    """
    State of LR0 parser. A LR0 state is a set of LR0 items.
    """

    def __init__(self) -> None:
        self.number = None
        self.items = set()
        self.is_final = False

    @staticmethod
    def from_items(items: Iterable[LR0Item]) -> "LR0State":
        """
        Create an LR0 state from a set of LR0 items.
        """
        state = LR0State()
        {state.add_item(item) for item in items}

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

    def __init__(self) -> None:
        self.number = None
        self.items = set()
        self.is_final = False

    @staticmethod
    def from_items(items: Iterable[LR1Item]) -> "LR1State":
        """
        Create an LR1 state from a set of LR1 items.
        """
        state = LR1State()
        {state.add_item(item) for item in items}

        return state

    def add_item(self, item: LR1Item) -> None:
        """
        Adds an item to the state.
        """
        self.items.add(item)

    def __repr__(self) -> str:
        return f"<LR1State: {self.number}>"
