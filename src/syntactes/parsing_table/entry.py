from syntactes.config import Symbol
from syntactes.generator._action import Action
from syntactes.generator._state import LR0State

type Row = dict[Symbol, list[Action]]


class Entry:
    """
    An entry of the parsing table. Holds the information of a transition from
    a state to another state via a symbol.
    """

    def __init__(self, from_state: LR0State, symbol: Symbol, action: Action) -> None:
        self.from_state = from_state
        self.symbol = symbol
        self.action = action

    def __repr__(self) -> str:
        return f"<Entry: {self!s}>"

    def __str__(self) -> str:
        return f"{self.from_state.number}, {self.action}, {self.symbol}"

    def __hash__(self) -> int:
        return hash((self.from_state, self.symbol, self.action))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Entry):
            return False

        return (
            self.from_state == other.from_state
            and self.symbol == other.symbol
            and self.action == other.action
        )
