from collections import deque
from typing import Iterable

from syntactes import Grammar, LR0Generator, SLRGenerator, Token
from syntactes._action import Action, ActionType
from syntactes._state import LR0State
from syntactes.parser import (
    ExecutablesRegistry,
    NotAcceptedError,
    ParserError,
    UnexpectedTokenError,
)
from syntactes.parsing_table import LR0ParsingTable


class LR0Parser:
    """
    Parses streams of tokens based on the configured parsing table.
    """

    def __init__(self, table: LR0ParsingTable) -> None:
        self._table = table
        self._token_stack: deque[Token] = deque()
        self._state_stack: deque[LR0State] = deque()
        self._token_stream: deque[Token] = deque()

    @staticmethod
    def from_grammar(grammar: Grammar) -> "LR0Parser":
        """
        Create a parser for the given grammar.
        """
        generator = LR0Generator(grammar)
        parsing_table = generator.generate()
        parser = LR0Parser(parsing_table)
        return parser

    def parse(self, stream: Iterable[Token]) -> None:
        """
        Parses the given stream of tokens. Expects the EOF token as the last one.

        Raises `syntactes.parser.UnexpectedTokenError` if an unexpected token is
        received.

        Raises `syntactes.parser.NotAcceptedError` if the stream of token has been
        parsed and the parser did not receive an accept action.
        """
        self._set_state(self._table.initial_state)
        self._token_stream.extend(stream)

        while len(self._token_stream) > 0:
            token = self._token_stream.popleft()
            self._apply_action(token, self._get_action(token))

        if token != Token.eof():
            self._raise(NotAcceptedError("Expected EOF token. "))

        if not self._get_state().is_final:
            actions = self._table.get(self._get_state())
            expected_tokens = [] if actions is None else list(actions.keys())
            self._raise(UnexpectedTokenError(Token.eof(), expected_tokens))

    def _apply_action(self, token: Token, action: Action) -> None:
        if action.action_type == ActionType.SHIFT:
            self._token_stack.append(token)
            self._set_state(action.actionable)
        elif action.action_type == ActionType.REDUCE:
            rule = action.actionable
            args = [self._token_stack.pop() for _ in reversed(rule.rhs)]
            self._token_stack.append(rule.lhs)

            {self._state_stack.pop() for _ in rule.rhs}

            executable = ExecutablesRegistry.get(rule)
            executable(*args)

            self._token_stream.appendleft(token)  # reduce actions do not consume tokenA

            shift = self._get_action(rule.lhs)
            self._set_state(shift.actionable)

    def _get_action(self, token: Token) -> Action:
        actions = self._table.get_actions(self._get_state(), token)
        if actions is None:
            actions = self._table.get(self._get_state())
            expected_tokens = [] if actions is None else list(actions.keys())
            self._raise(UnexpectedTokenError(token, expected_tokens))

        action = self._resolve_conflict(actions)
        return action

    def _resolve_conflict(self, actions: list[Action]) -> Action:
        return actions[0]

    def _set_state(self, state: LR0State) -> None:
        self._state_stack.append(state)

    def _get_state(self) -> LR0State:
        return self._state_stack[-1]

    def _cleanup(self) -> None:
        self._token_stack.clear()
        self._state_stack.clear()
        self._token_stream.clear()

    def _raise(self, error: ParserError) -> None:
        self._cleanup()
        raise error from None


class SLRParser(LR0Parser):
    """
    Parses streams of tokens based on the configured parsing table.
    """

    @staticmethod
    def from_grammar(grammar: Grammar) -> "SLRParser":
        """
        Create a parser for the given grammar.
        """
        generator = SLRGenerator(grammar)
        parsing_table = generator.generate()
        parser = SLRParser(parsing_table)
        return parser
