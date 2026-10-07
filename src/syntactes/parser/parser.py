from abc import ABC
from collections.abc import Callable, Iterable
from typing import cast

from syntactes import (
    Grammar,
    LR0Generator,
    LR1Generator,
    Rule,
    SLRGenerator,
    Token,
)
from syntactes._action import Action, ActionType
from syntactes._state import LR0State
from syntactes.parser import (
    NotAcceptedError,
    UnexpectedTokenError,
)
from syntactes.parsing_table import ParsingTable

type Executable = Callable[..., object]


def _do_nothing(*_: Token) -> None:
    return None


class Parser(ABC):
    """
    Base class of the LR parsers. Parses a stream of tokens with a parsing table,
    and calls the callbacks registered with `execute_on` on each reduction.
    """

    generator_cls: type

    def __init__(self, table: ParsingTable) -> None:
        self._table = table
        self._executables: dict[Rule, Executable] = {}

    @classmethod
    def from_grammar(cls, grammar: Grammar) -> "Parser":
        """
        Create a parser for the given grammar.
        """
        generator = cls.generator_cls(grammar)
        parsing_table = generator.generate()
        parser = cls(parsing_table)
        return parser

    def execute_on[F: Executable](self, rule: Rule) -> Callable[[F], F]:
        """
        Decorate a function to be executed when this parser reduces by `rule`.

        The function is called with one token per right-hand side symbol of the
        rule, and returns the value of the left-hand side token. The decorated
        function is returned unchanged.

        Raises `ValueError` if `rule` is not a rule of the parser's grammar.
        """
        if rule not in self._table.grammar.rules:
            raise ValueError(f"Rule '{rule}' is not in the parser's grammar.")

        def executable_decorator(executable_fn: F) -> F:
            self._executables[rule] = executable_fn
            return executable_fn

        return executable_decorator

    def parse(self, stream: Iterable[Token]) -> object:
        """
        Parses the given stream of tokens. Expects the EOF token as the last one.

        On each reduction the callback registered for the rule is called with one
        token per right-hand side symbol, in order. Its return value becomes the
        `value` of the token pushed for the left-hand side. A rule without a
        callback pushes a token whose value is None.

        On accept the starting rule's callback is called with its right-hand side
        tokens except the trailing EOF, and its return value is returned. Without
        a callback for the starting rule, returns None.

        Raises `syntactes.parser.UnexpectedTokenError` if an unexpected token is
        received.

        Raises `syntactes.parser.NotAcceptedError` if the stream of tokens ends
        before the parser receives an accept action.
        """
        states: list[LR0State] = [self._table.initial_state]
        tokens: list[Token] = []

        tokens_in = iter(stream)
        token = next(tokens_in, None)

        while token is not None:
            action = self._get_action(states[-1], token)

            if action.action_type == ActionType.SHIFT:
                tokens.append(token)
                states.append(cast(LR0State, action.actionable))
                token = next(tokens_in, None)
            elif action.action_type == ActionType.REDUCE:
                # Reduce actions do not consume the token.
                rule = cast(Rule, action.actionable)
                rhs_len = 0 if rule.is_empty() else rule.rhs_len
                args = self._pop(tokens, rhs_len)
                self._pop(states, rhs_len)

                value = self._executable(rule)(*args)

                tokens.append(Token(rule.lhs.symbol, False, value))
                shift = self._get_action(states[-1], rule.lhs)
                states.append(cast(LR0State, shift.actionable))
            elif action.action_type == ActionType.ACCEPT:
                extra = next(tokens_in, None)
                if extra is not None:
                    raise UnexpectedTokenError(extra, [])

                starting_rule = self._table.grammar.starting_rule
                args = self._pop(tokens, starting_rule.rhs_len - 1)
                return self._executable(starting_rule)(*args)

        raise NotAcceptedError("Expected EOF token. ")

    def _executable(self, rule: Rule) -> Executable:
        return self._executables.get(rule, _do_nothing)

    @staticmethod
    def _pop[T](stack: list[T], count: int) -> list[T]:
        """
        Pops the top `count` elements of the stack and returns them in stack order.
        """
        popped = stack[len(stack) - count :]
        del stack[len(stack) - count :]
        return popped

    def _get_action(self, state: LR0State, token: Token) -> Action:
        actions = self._table.get_actions(state, token)
        if actions is None:
            raise UnexpectedTokenError(token, self._expected_tokens(state))

        return self._resolve_conflict(actions)

    def _expected_tokens(self, state: LR0State) -> list[Token]:
        """
        Returns the terminals that have an action in the given state, sorted.
        """
        row = self._table.get(state) or {}
        return sorted(token for token in row if token.is_terminal)

    def _resolve_conflict(self, actions: list[Action]) -> Action:
        """
        Picks one of the actions of a table cell. Accept wins over shift, shift
        wins over reduce, and among reduces the lowest rule number wins.
        """
        return min(actions, key=self._action_priority)

    @staticmethod
    def _action_priority(action: Action) -> tuple[int, int]:
        if action.action_type == ActionType.ACCEPT:
            return (0, 0)

        if action.action_type == ActionType.SHIFT:
            return (1, 0)

        return (2, cast(Rule, action.actionable).number)


class LR0Parser(Parser):
    """
    Parser that uses an LR0 parsing table.
    """

    generator_cls = LR0Generator


class SLRParser(Parser):
    """
    Parser that uses an SLR parsing table.
    """

    generator_cls = SLRGenerator


class LR1Parser(Parser):
    """
    Parser that uses an LR1 parsing table.
    """

    generator_cls = LR1Generator
