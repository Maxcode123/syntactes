from syntactes import Grammar, Token
from syntactes._action import Action, ActionType
from syntactes._item import LR0Item
from syntactes._state import LR0State
from syntactes.table import Entry, LR0ParsingTable, SLRParsingTable


class LR0Generator:
    """
    Generator of LR0 parsing tables.
    """

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar

    def generate(self) -> LR0ParsingTable:
        """
        Generates an LR0 parsing table for the configured grammar.
        """
        states, shift_entries = self._create_states_and_shift_entries()
        reduce_entries = self._create_reduce_entries(states)

        entries = shift_entries | reduce_entries

        table = LR0ParsingTable.from_entries(entries, self.grammar)

        return table

    def closure(self, items: set[LR0Item]) -> set[LR0Item]:
        """
        Computes and returns the closure for the given set of items.

        The closure operation adds more items to a set of items when there
        is a dot to the left of a non-terminal symbol.

        e.g.
        for any item S -> . E in the given items, closure adds E -> . T
        and T -> . x, where E -> T and T -> x are production rules.
        """
        _set = {item for item in items}

        for item in items:
            if item.dot_is_last():
                continue

            new_items = self._get_related_items(item.after_dot)
            _set |= new_items

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

    def get_states(self) -> set[LR0State]:
        """
        Returns the set of automaton states for the configured grammar.
        """
        states, _ = self._create_states_and_shift_entries()
        return states

    def _first(self, symbol: Token) -> set[Token]:
        """
        Computes and returns the FIRST set for the given symbol.

        The FIRST set of a symbol 'G' is the set of terminal symbols that are
        first in the right-hand side of a rule where 'G' is the left-hand side.

        e.g. 't', 'k' and 'a' would be the FIRST set of G for the below rules:
        1. G -> t
        2. G -> kM
        3. G -> T
        4. T -> a
        where M is either terminal or non-terminal and T is non-terminal.
        'a' would be included in the FIRST set because if rule 4 is substituted in
        rule 3, 'a' (which is a terminal) could be derived from 'G'.
        """
        if symbol.is_terminal:
            return {symbol}

        _set: set[Token] = set()

        for rule in self.grammar.rules:
            if rule.lhs != symbol:
                continue

            if rule.rhs[0].is_terminal:
                _set.add(rule.rhs[0])
            elif rule.rhs_len == 1:
                _set |= self._first(rule.rhs[0])

        return _set

    def _follow(self, symbol: Token) -> set[Token]:
        """
        Computes and returns the FOLLOW set for the given symbol.

        The FOLLOW set of a symbol 'G' is the set of terminals that can immediately
        follow 'G' in a rule.
        """
        if symbol.is_terminal:
            return set()

        _set: set[Token] = set()

        for rule in self.grammar.rules:
            for i, s in enumerate(rule.rhs):
                if s != symbol:
                    continue

                if i == rule.rhs_len - 1:
                    if rule.lhs == symbol:
                        continue

                    _set |= self._follow(rule.lhs)
                else:
                    _set |= self._first(rule.rhs[i + 1])

        return _set

    def _get_related_items(self, symbol: Token) -> set[LR0Item]:
        """
        e.g. the items X -> .g, Y -> .p would be returned for the below grammar rules:
        1. X -> g
        2. X -> Y
        3. Y -> p
        where 'g' and 'p' are terminals.
        """
        _set: set[LR0Item] = set()

        for rule in self.grammar.rules:
            if rule.lhs == symbol:
                _set.add(LR0Item(rule, 0))

                if rule.rhs_len == 1 and not rule.rhs[0].is_terminal:
                    _set |= self._get_related_items(rule.rhs[0])

        return _set

    def _create_states_and_shift_entries(self) -> tuple[set[LR0State], set[Entry]]:
        """
        Computes and returns the states and entries for shift actions.
        """
        states, entries = dict(), set()

        initial_items = self.closure({LR0Item(self.grammar.starting_rule, 0)})
        initial_state = LR0State.from_items(initial_items)
        initial_state.set_number(1)
        states[initial_state] = 1

        _states, _entries = dict(), set()
        while (_states, _entries) != (states, entries):
            _states = {s: n for s, n in states.items()}
            _entries = {e for e in entries}
            states, entries = self._extend_states_and_shift_entries(_states, _entries)

        return set(states.keys()), entries

    def _extend_states_and_shift_entries(
        self, states: dict[LR0State, int], entries: set[Entry]
    ) -> tuple[dict[LR0State, int], set[Entry]]:
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
            for item in state.items:
                if item.dot_is_last():
                    continue

                if item.after_dot == EOF:
                    state.set_final()
                    continue

                new_items = self.goto(state.items, item.after_dot)

                if len(new_items) == 0:
                    continue

                new = LR0State.from_items(new_items)

                number = _states.setdefault(new, len(_states) + 1)
                new.set_number(number)

                _entries.add(Entry(state, item.after_dot, Action.shift(new)))

        return _states, _entries

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
    def generate(self) -> SLRParsingTable:
        """
        Generates an SLR parsing table for the configured grammar.
        """
        states, shift_entries = self._create_states_and_shift_entries()
        reduce_entries = self._create_reduce_entries(states)

        entries = shift_entries | reduce_entries

        table = SLRParsingTable.from_entries(entries, self.grammar)

        return table

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
