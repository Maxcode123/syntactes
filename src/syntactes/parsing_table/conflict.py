from enum import Enum

from syntactes import Token
from syntactes._action import Action, ActionType
from syntactes._state import LR0State


class ConflictType(Enum):
    """
    The kinds of actions that conflict in a cell of a parsing table.
    """

    SHIFT_SHIFT = "shift/shift"
    SHIFT_REDUCE = "shift/reduce"
    REDUCE_REDUCE = "reduce/reduce"
    NO_CONFLICT = "NO_CONFLICT"


class Conflict:
    """
    A cell of a parsing table with more than one action: the `actions` for
    `token` in `state`.
    """

    def __init__(self, state: LR0State, token: Token, actions: list[Action]) -> None:
        self.state = state
        self.token = token
        self.actions = actions
        self._conflict_type = None

    def pretty_str(self) -> str:
        """
        Returns a pretty-formatted string with conflict details.
        """
        string = f"{self.conflict_type.value} conflict in state {self.state}\n"
        string += f"Available actions on input token '{self.token}':\n"
        for action in self.actions:
            if action.action_type == ActionType.SHIFT:
                string += f"shift to {action.actionable}\n"
            elif action.action_type == ActionType.REDUCE:
                string += f"reduce by {action.actionable}\n"
            else:
                string += f"{action.action_type}, {action.actionable}\n"

        return string

    @property
    def conflict_type(self) -> ConflictType:
        """
        The kind of the conflict, from the types of its actions.
        """
        if self._conflict_type is None:
            self._conflict_type = self._create_type()

        return self._conflict_type

    def _create_type(self) -> ConflictType:
        if not len(self.actions) > 1:
            return ConflictType.NO_CONFLICT

        action_types = {a.action_type for a in self.actions}

        if ActionType.SHIFT not in action_types:
            if ActionType.REDUCE not in action_types:
                return ConflictType.NO_CONFLICT

            return ConflictType.REDUCE_REDUCE

        if ActionType.REDUCE not in action_types:
            return ConflictType.SHIFT_SHIFT

        return ConflictType.SHIFT_REDUCE

    def __repr__(self) -> str:
        return f"<Conflict: {self!s}>"

    def __str__(self) -> str:
        return f"{self.state}, {self.token}, {self.actions}"
