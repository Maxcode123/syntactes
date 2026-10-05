from abc import ABC
from collections.abc import Iterable
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
    ExecutablesRegistry,
    NotAcceptedError,
    UnexpectedTokenError,
)
from syntactes.parsing_table import ParsingTable


class Parser(ABC):
    generator_cls: type

    def __init__(self, table: ParsingTable) -> None:
        self._table = table

    @classmethod
    def from_grammar(cls, grammar: Grammar) -> "Parser":
        """
        Create a parser for the given grammar.
        """
        generator = cls.generator_cls(grammar)
        parsing_table = generator.generate()
        parser = cls(parsing_table)
        return parser

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
                args = self._pop(tokens, rule.rhs_len)
                self._pop(states, rule.rhs_len)

                value = ExecutablesRegistry.get(rule)(*args)

                tokens.append(Token(rule.lhs.symbol, False, value))
                shift = self._get_action(states[-1], rule.lhs)
                states.append(cast(LR0State, shift.actionable))
            elif action.action_type == ActionType.ACCEPT:
                extra = next(tokens_in, None)
                if extra is not None:
                    raise UnexpectedTokenError(extra, [])

                starting_rule = self._table.grammar.starting_rule
                args = self._pop(tokens, starting_rule.rhs_len - 1)
                return ExecutablesRegistry.get(starting_rule)(*args)

        raise NotAcceptedError("Expected EOF token. ")

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
    generator_cls = LR0Generator


class SLRParser(Parser):
    generator_cls = SLRGenerator


class LR1Parser(Parser):
    generator_cls = LR1Generator
