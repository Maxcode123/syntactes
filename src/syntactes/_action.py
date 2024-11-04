from typing import Protocol
from enum import Enum


class Actionable(Protocol):
    """
    State or Rule.
    """

    number: int


class ActionType(Enum):
    SHIFT = "SHIFT"
    REDUCE = "REDUCE"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"

    def abbreviated(self) -> str:
        """
        Returns an abbreviated version of the action type.
        """
        if self == self.SHIFT:
            return "s"
        if self == self.REDUCE:
            return "r"
        if self == self.ACCEPT:
            return "a"
        if self == self.REJECT:
            return "e"


class Action:
    """
    Parsing action. Contains data relevant to the actionable object (State or Rule)
    and the relevant action to be applied.

    The `actionable_number` refers to the state number for `State` actionables and
    to the rule number for `Rule` actionables.
    """

    def __init__(self, actionable: Actionable, action_type: ActionType) -> None:
        self.actionable = actionable
        self.action_type = action_type

    @staticmethod
    def shift(state: Actionable) -> "Action":
        """
        Create a shift action to the given state.
        """
        return Action(state, ActionType.SHIFT)

    @staticmethod
    def reduce(rule: Actionable) -> "Action":
        """
        Create a reduce action of the given rule.
        """
        return Action(rule, ActionType.REDUCE)

    @staticmethod
    def accept() -> "Action":
        """
        Create an accept action.
        """
        return Action(None, ActionType.ACCEPT)

    def __repr__(self) -> str:
        return f"<Action: {self}>"

    def __str__(self) -> str:
        if self.action_type in {ActionType.ACCEPT, ActionType.REJECT}:
            return str(self.action_type.abbreviated())

        return f"{self.action_type.abbreviated()}{self.actionable.number}"

    def __hash__(self) -> int:
        return hash((self.actionable, self.action_type))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Action):
            return False

        return (
            self.actionable == other.actionable
            and self.action_type == other.action_type
        )
