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
    """
    Base class of the parsing table generators. Computes the FIRST and FOLLOW
    sets of the grammar, and builds the automaton states and the table.
    """

    table_cls: type[ParsingTable]
    state_cls: type[StateT]
    item_cls: type[ItemT]

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self._rules = tuple(grammar.rules)
        self._rule_indices = {rule: i for i, rule in enumerate(self._rules)}
        self._rules_by_lhs: dict[Token, list[Rule]] = {}
        for rule in self._rules:
            self._rules_by_lhs.setdefault(rule.lhs, []).append(rule)
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

        # Duplicates are dropped and the order is kept, so that the actions in
        # each cell of the table come in the same order on every run.
        entries = list(dict.fromkeys(shift_entries + reduce_entries))

        table = self.table_cls.from_entries(entries, self.grammar)

        return table

    def get_states(self) -> set[StateT]:
        """
        Returns the set of automaton states for the configured grammar.
        """
        states, _ = self._create_states_and_shift_entries()
        return set(states)

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

    def _create_states_and_shift_entries(self) -> tuple[list[StateT], list[Entry]]:
        """
        Computes and returns the states, in the order of their numbers, and the
        entries for shift actions.

        States are discovered breadth-first and numbered in discovery order. Items
        and symbols are visited in a fixed order, so the numbering doesn't depend
        on set iteration order.
        """
        initial_state = self.state_cls.from_items(self._create_initial_items())
        initial_state.set_number(1)

        known: dict[StateT, StateT] = {initial_state: initial_state}
        # The kernel of a goto (its items before closure) determines the state,
        # so a kernel seen before needs no closure.
        by_kernel: dict[frozenset[ItemT], StateT] = {}
        states = [initial_state]
        entries: list[Entry] = []

        EOF = Token.eof()
        for state in states:
            # A state's items are of the generator's item type, e.g. LR1State
            # holds LR1Items, but the shared state base class can't express that.
            items = cast(set[ItemT], state.items)

            kernels: dict[Token, list[ItemT]] = {}
            for item in self._sorted_items(items):
                after_dot = item.after_dot
                if after_dot is None:
                    continue

                if after_dot == EOF:
                    state.set_final()
                    continue

                kernels.setdefault(after_dot, []).append(self._advance(item))

            for symbol, kernel_items in kernels.items():
                kernel = frozenset(kernel_items)
                target = by_kernel.get(kernel)
                if target is None:
                    new = self.state_cls.from_items(self.closure(set(kernel)))
                    target = known.get(new)
                    if target is None:
                        new.set_number(len(states) + 1)
                        known[new] = new
                        states.append(new)
                        target = new

                    by_kernel[kernel] = target

                entries.append(Entry(state, symbol, Action.shift(target)))

        return states, entries

    def _sorted_items(self, items: set[ItemT]) -> list[ItemT]:
        return sorted(items, key=self._item_key)

    def _item_key(self, item: ItemT) -> tuple[int, int, str]:
        """
        Returns the key that orders items by rule, then dot position.
        """
        return (self._rule_indices[item.rule], item.position, "")

    @abstractmethod
    def _advance(self, item: ItemT) -> ItemT:
        """
        Returns the item with the dot moved one symbol to the right.
        """
        raise NotImplementedError()

    @abstractmethod
    def _create_initial_items(self) -> set[ItemT]:
        raise NotImplementedError()

    @abstractmethod
    def _create_reduce_entries(self, states: list[StateT]) -> list[Entry]:
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
        _set = {self._advance(item) for item in items if item.after_dot == token}
        return self.closure(_set)

    def _advance(self, item: LR0Item) -> LR0Item:
        return LR0Item(item.rule, item.position + 1)

    def _get_related_items(self, symbol: Token) -> set[LR0Item]:
        """
        Returns the initial items of the rules for the given symbol.

        e.g. the items X -> . g and X -> . Y would be returned for symbol X and
        the below grammar rules:
        1. X -> g
        2. X -> Y
        3. Y -> p
        """
        return {LR0Item(rule, 0) for rule in self._rules_by_lhs.get(symbol, [])}

    def _create_initial_items(self) -> set[LR0Item]:
        return self.closure({LR0Item(self.grammar.starting_rule, 0)})

    def _create_reduce_entries(self, states: list[LR0State]) -> list[Entry]:
        """
        Computes and returns the entries for reduce actions and the accept action.
        """
        entries: list[Entry] = []
        null = Token.null()
        terminals = sorted(
            t for t in self.grammar.tokens if t.is_terminal and t != null
        )

        for state in states:
            for item in self._sorted_items(state.items):
                if item.after_dot == Token.eof():
                    entries.append(Entry(state, Token.eof(), Action.accept()))

                if not item.dot_is_last():
                    continue

                for token in terminals:
                    entries.append(Entry(state, token, Action.reduce(item.rule)))

        return entries


class SLRGenerator(LR0Generator):
    """
    Generator of SLR parsing tables. Like LR0, but only reduces on the tokens
    that can follow the rule's left-hand side.
    """

    table_cls = SLRParsingTable

    def _create_reduce_entries(self, states: list[LR0State]) -> list[Entry]:
        """
        Computes and returns the entries for reduce actions and the accept action.
        """
        entries: list[Entry] = []

        for state in states:
            for item in self._sorted_items(state.items):
                if item.after_dot == Token.eof():
                    entries.append(Entry(state, Token.eof(), Action.accept()))

                if not item.dot_is_last():
                    continue

                for token in sorted(self._follow(item.rule.lhs)):
                    entries.append(Entry(state, token, Action.reduce(item.rule)))

        return entries


class LR1Generator(Generator[LR1Item, LR1State]):
    """
    Generator of LR1 parsing tables. Each item carries a lookahead token, and
    rules are only reduced on their lookaheads.
    """

    table_cls = LR1ParsingTable
    state_cls = LR1State
    item_cls = LR1Item

    def __init__(self, grammar: Grammar) -> None:
        super().__init__(grammar)
        self._related_items_cache: dict[
            tuple[Token, tuple[Token, ...], Token], set[LR1Item]
        ] = {}

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
        _set = {self._advance(item) for item in items if item.after_dot == token}
        return self.closure(_set)

    def _advance(self, item: LR1Item) -> LR1Item:
        return LR1Item(item.rule, item.position + 1, item.lookahead_token)

    def _get_related_items(
        self, symbol: Token, rest: tuple[Token, ...], lookahead_token: Token
    ) -> set[LR1Item]:
        """
        Returns the initial items of the rules for the given symbol, with every
        lookahead in FIRST(rest lookahead_token).
        """
        key = (symbol, rest, lookahead_token)
        related = self._related_items_cache.get(key)
        if related is None:
            lookaheads = self._first(*rest, lookahead_token)
            related = {
                LR1Item(rule, 0, lookahead)
                for rule in self._rules_by_lhs.get(symbol, [])
                for lookahead in lookaheads
            }
            self._related_items_cache[key] = related

        return related

    def _create_reduce_entries(self, states: list[LR1State]) -> list[Entry]:
        """
        Computes and returns the entries for reduce actions and the accept action.
        """
        entries: list[Entry] = []

        for state in states:
            for item in self._sorted_items(state.items):
                if item.after_dot == Token.eof():
                    entries.append(Entry(state, Token.eof(), Action.accept()))

                if not item.dot_is_last():
                    continue

                entries.append(
                    Entry(state, item.lookahead_token, Action.reduce(item.rule))
                )

        return entries

    def _item_key(self, item: LR1Item) -> tuple[int, int, str]:
        """
        Returns the key that orders items by rule, then dot position, then
        lookahead.
        """
        return (
            self._rule_indices[item.rule],
            item.position,
            item.lookahead_token.symbol,
        )

    def _create_initial_items(self) -> set[LR1Item]:
        return self.closure({LR1Item(self.grammar.starting_rule, 0, Token.eof())})
