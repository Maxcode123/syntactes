from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import cast

from syntactes import Grammar, Rule, Token
from syntactes._action import Action
from syntactes._item import LR0Item, LR1Item
from syntactes._state import LR0State, LR1State
from syntactes.parsing_table import (
    Entry,
    LR0ParsingTable,
    LR1ParsingTable,
    ParsingTable,
    SLRParsingTable,
)


class Generator[ItemT: LR0Item, StateT: LR0State](ABC):
    table_cls: type[ParsingTable]
    state_cls: type[StateT]
    item_cls: type[ItemT]

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self._rules = tuple(grammar.rules)
        self._nullable = self._compute_nullable()
        self._first_sets = self._compute_first_sets()
        self._follow_sets = self._compute_follow_sets()

    @abstractmethod
    def closure(self, items: set[ItemT]) -> set[ItemT]:
        raise NotImplementedError()

    @abstractmethod
    def goto(self, items: set[ItemT], token: Token) -> set[ItemT]:
        raise NotImplementedError()

    def generate(self) -> ParsingTable:
        """
        Generates an parsing table for the configured grammar.
        """
        states, shift_entries = self._create_states_and_shift_entries()
        reduce_entries = self._create_reduce_entries(states)

        entries = shift_entries | reduce_entries

        table = self.table_cls.from_entries(entries, self.grammar)

        return table

    def get_states(self) -> set[StateT]:
        """
        Returns the set of automaton states for the configured grammar.
        """
        states, _ = self._create_states_and_shift_entries()
        return states

    def _first(self, *symbols: Token) -> set[Token]:
        """
        Returns the FIRST set of the given sequence of symbols.

        The FIRST set of a sequence is the set of terminals that can begin a
        string derived from it. ε never appears in it; whether the whole sequence
        can derive the empty string is a question for the nullable set.

        e.g. for the rules below, FIRST(G) is {t, k, a}:
        1. G -> t
        2. G -> k M
        3. G -> T
        4. T -> a
        If X can derive the empty string, FIRST(X Y) also includes FIRST(Y).
        """
        return self._first_of(symbols, self._first_sets)

    def _follow(self, symbol: Token) -> set[Token]:
        """
        Returns the FOLLOW set of the given symbol.

        The FOLLOW set of a non-terminal is the set of terminals that can appear
        immediately after it in some derivation. Terminals have an empty FOLLOW
        set.
        """
        return set(self._follow_sets.get(symbol, set()))

    @staticmethod
    def _rhs(rule: Rule) -> tuple[Token, ...]:
        """
        Returns the right-hand side of the rule without ε symbols.
        """
        null = Token.null()
        return tuple(s for s in rule.rhs if s != null)

    def _first_of(
        self, symbols: Iterable[Token], first_sets: dict[Token, set[Token]]
    ) -> set[Token]:
        result: set[Token] = set()
        null = Token.null()

        for symbol in symbols:
            if symbol == null:
                continue

            if symbol.is_terminal:
                result.add(symbol)
                return result

            result |= first_sets.get(symbol, set())
            if symbol not in self._nullable:
                return result

        return result

    def _compute_nullable(self) -> set[Token]:
        """
        Computes the set of non-terminals that can derive the empty string.
        """
        nullable: set[Token] = set()

        changed = True
        while changed:
            changed = False
            for rule in self._rules:
                if rule.lhs in nullable:
                    continue

                if all(s in nullable for s in self._rhs(rule)):
                    nullable.add(rule.lhs)
                    changed = True

        return nullable

    def _compute_first_sets(self) -> dict[Token, set[Token]]:
        """
        Computes the FIRST set of every non-terminal, as a fixpoint over all rules.
        """
        first_sets: dict[Token, set[Token]] = {rule.lhs: set() for rule in self._rules}

        changed = True
        while changed:
            changed = False
            for rule in self._rules:
                new = self._first_of(self._rhs(rule), first_sets)
                if not new <= first_sets[rule.lhs]:
                    first_sets[rule.lhs] |= new
                    changed = True

        return first_sets

    def _compute_follow_sets(self) -> dict[Token, set[Token]]:
        """
        Computes the FOLLOW set of every non-terminal, as a fixpoint over all rules.
        """
        follow_sets: dict[Token, set[Token]] = {rule.lhs: set() for rule in self._rules}

        changed = True
        while changed:
            changed = False
            for rule in self._rules:
                rhs = self._rhs(rule)
                for i, symbol in enumerate(rhs):
                    if symbol.is_terminal:
                        continue

                    rest = rhs[i + 1 :]
                    new = self._first(*rest)
                    if all(s in self._nullable for s in rest):
                        new |= follow_sets[rule.lhs]

                    follow = follow_sets.setdefault(symbol, set())
                    if not new <= follow:
                        follow |= new
                        changed = True

        return follow_sets

    def _create_states_and_shift_entries(self) -> tuple[set[StateT], set[Entry]]:
        """
        Computes and returns the states and entries for shift actions.
        """
        states, entries = {}, set()

        initial_items = self._create_initial_items()
        initial_state = self.state_cls.from_items(initial_items)
        initial_state.set_number(1)
        states[initial_state] = 1

        _states, _entries = {}, set()
        while (_states, _entries) != (states, entries):
            _states = {s: n for s, n in states.items()}
            _entries = {e for e in entries}
            states, entries = self._extend_states_and_shift_entries(_states, _entries)

        return set(states.keys()), entries

    def _extend_states_and_shift_entries(
        self, states: dict[StateT, int], entries: set[Entry]
    ) -> tuple[dict[StateT, int], set[Entry]]:
        """
        Extends states and entries following the below algorithm:

        ```
        for each state S in states
            for each item A -> a.Xb in S
                J = goto(S, X)
                states.add(J)
                entries.add((S->J, X))
        ```
        """
        _states = {s: n for s, n in states.items()}
        _entries = {e for e in entries}

        EOF = Token.eof()
        for state in states:
            # A state's items are of the generator's item type, e.g. LR1State
            # holds LR1Items, but the shared state base class can't express that.
            items = cast(set[ItemT], state.items)
            for item in items:
                after_dot = item.after_dot
                if after_dot is None:
                    continue

                if after_dot == EOF:
                    state.set_final()
                    continue

                new_items = self.goto(items, after_dot)

                if len(new_items) == 0:
                    continue

                new = self.state_cls.from_items(new_items)

                number = _states.setdefault(new, len(_states) + 1)
                new.set_number(number)

                _entries.add(Entry(state, after_dot, Action.shift(new)))

        return _states, _entries

    @abstractmethod
    def _create_initial_items(self) -> set[ItemT]:
        raise NotImplementedError()

    @abstractmethod
    def _create_reduce_entries(self, states: set[StateT]) -> set[Entry]:
        raise NotImplementedError()


class LR0Generator(Generator[LR0Item, LR0State]):
    """
    Generator of LR0 parsing tables.
    """

    table_cls = LR0ParsingTable
    state_cls = LR0State
    item_cls = LR0Item

    def closure(self, items: set[LR0Item]) -> set[LR0Item]:
        """
        Computes and returns the closure for the given set of items.

        The closure operation adds more items to a set of items when there
        is a dot to the left of a non-terminal symbol.

        e.g.
        for any item S -> . E in the given items, closure adds E -> . T
        and T -> . x, where E -> T and T -> x are production rules.
        """
        _set = set(items)
        worklist = list(items)

        while worklist:
            item = worklist.pop()
            after_dot = item.after_dot
            if after_dot is None or after_dot.is_terminal:
                continue

            for new_item in self._get_related_items(after_dot):
                if new_item not in _set:
                    _set.add(new_item)
                    worklist.append(new_item)

        return _set

    def goto(self, items: set[LR0Item], token: Token) -> set[LR0Item]:
        """
        Computes and returns the GOTO set for the given set of items.

        The goto operation creates a set where all items have the dot past the
        given symbol.
        """
        _set: set[LR0Item] = set()

        for item in items:
            if item.dot_is_last() or item.after_dot != token:
                continue

            next_item = LR0Item(item.rule, item.position + 1)
            _set.add(next_item)

        return self.closure(_set)

    def _get_related_items(self, symbol: Token) -> set[LR0Item]:
        """
        Returns the initial items of the rules for the given symbol.

        e.g. the items X -> . g and X -> . Y would be returned for symbol X and
        the below grammar rules:
        1. X -> g
        2. X -> Y
        3. Y -> p
        """
        return {LR0Item(rule, 0) for rule in self._rules if rule.lhs == symbol}

    def _create_initial_items(self) -> set[LR0Item]:
        return self.closure({LR0Item(self.grammar.starting_rule, 0)})

    def _create_reduce_entries(self, states: set[LR0State]) -> set[Entry]:
        """
        Computes and returns the entries for reduce actions and the accept action.
        """
        entries: set[Entry] = set()

        for state in states:
            for item in state.items:
                if item.after_dot == Token.eof():
                    entries.add(Entry(state, Token.eof(), Action.accept()))

                if not item.dot_is_last():
                    continue

                for token in self.grammar.tokens:
                    if token.is_terminal:
                        entries.add(Entry(state, token, Action.reduce(item.rule)))

        return entries


class SLRGenerator(LR0Generator):
    table_cls = SLRParsingTable

    def _create_reduce_entries(self, states: set[LR0State]) -> set[Entry]:
        """
        Computes and returns the entries for reduce actions and the accept action.
        """
        entries: set[Entry] = set()

        for state in states:
            for item in state.items:
                if item.after_dot == Token.eof():
                    entries.add(Entry(state, Token.eof(), Action.accept()))

                if not item.dot_is_last():
                    continue

                for token in self._follow(item.rule.lhs):
                    entries.add(Entry(state, token, Action.reduce(item.rule)))

        return entries


class LR1Generator(Generator[LR1Item, LR1State]):
    table_cls = LR1ParsingTable
    state_cls = LR1State
    item_cls = LR1Item

    def closure(self, items: set[LR1Item]) -> set[LR1Item]:
        """
        Computes and returns the closure for the given set of items.

        The closure operation adds more items to a set of items when there
        is a dot to the left of a non-terminal symbol.

        e.g. for an item A -> α . B β, a it adds B -> . γ, b for every rule
        B -> γ and every terminal b in FIRST(β a).
        """
        _set = set(items)
        worklist = list(items)

        while worklist:
            item = worklist.pop()
            after_dot = item.after_dot
            if after_dot is None or after_dot.is_terminal:
                continue

            rest = item.rule.rhs[item.position + 1 :]
            for new_item in self._get_related_items(
                after_dot, rest, item.lookahead_token
            ):
                if new_item not in _set:
                    _set.add(new_item)
                    worklist.append(new_item)

        return _set

    def goto(self, items: set[LR1Item], token: Token) -> set[LR1Item]:
        """
        Computes and returns the GOTO set for the given set of items.

        The goto operation creates a set where all items have the dot past the
        given symbol.
        """
        _set: set[LR1Item] = set()

        for item in items:
            if item.dot_is_last() or item.after_dot != token:
                continue

            next_item = LR1Item(item.rule, item.position + 1, item.lookahead_token)
            _set.add(next_item)

        return self.closure(_set)

    def _get_related_items(
        self, symbol: Token, rest: tuple[Token, ...], lookahead_token: Token
    ) -> set[LR1Item]:
        """
        Returns the initial items of the rules for the given symbol, with every
        lookahead in FIRST(rest lookahead_token).
        """
        lookaheads = self._first(*rest, lookahead_token)

        return {
            LR1Item(rule, 0, lookahead)
            for rule in self._rules
            if rule.lhs == symbol
            for lookahead in lookaheads
        }

    def _create_reduce_entries(self, states: set[LR1State]) -> set[Entry]:
        """
        Computes and returns the entries for reduce actions and the accept action.
        """
        entries: set[Entry] = set()

        for state in states:
            for item in state.items:
                if item.after_dot == Token.eof():
                    entries.add(Entry(state, Token.eof(), Action.accept()))

                if not item.dot_is_last():
                    continue

                entries.add(
                    Entry(state, item.lookahead_token, Action.reduce(item.rule))
                )

        return entries

    def _create_initial_items(self) -> set[LR1Item]:
        return self.closure({LR1Item(self.grammar.starting_rule, 0, Token.eof())})
