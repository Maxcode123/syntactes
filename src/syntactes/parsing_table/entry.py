from typing import TypeAlias

from syntactes import Token
from syntactes._action import Action
from syntactes._state import LR0State

Row: TypeAlias = dict[Token, list[Action]]


class Entry:
    """
    An entry of the parsing table. Holds the information of a transition from
    a state to another state via a symbol.
    """

    def __init__(self, from_state: LR0State, token: Token, action: Action) -> None:
        self.from_state = from_state
        self.token = token
        self.action = action

    def __repr__(self) -> str:
        return f"<Entry: {str(self)}>"

    def __str__(self) -> str:
        return f"{self.from_state.number}, {self.action}, {self.token}"

    def __hash__(self) -> int:
        return hash((self.from_state, self.token, self.action))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Entry):
            return False

        return (
            self.from_state == other.from_state
            and self.token == other.token
            and self.action == other.action
        )
