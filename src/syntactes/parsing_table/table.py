from collections.abc import Iterable
from typing import Protocol, Self

from syntactes.config import Grammar, Symbol
from syntactes.generator._action import Action
from syntactes.generator._state import LR0State
from syntactes.parsing_table import Conflict, Entry

type Row = dict[Symbol, list[Action]]


class ParsingTable(Protocol):
    """
    The interface of the parsing tables that generators create and parsers use.
    """

    rows: dict[LR0State, Row]

    @property
    def grammar(self) -> Grammar: ...

    @property
    def initial_state(self) -> LR0State: ...

    @classmethod
    def from_entries(
        cls, entries: Iterable[Entry], grammar: Grammar
    ) -> "ParsingTable": ...

    def get(self, state: LR0State) -> Row | None: ...

    def get_actions(self, state: LR0State, symbol: Symbol) -> list[Action] | None: ...

    def pretty_str(self) -> str: ...

    def conflicts(self) -> list[Conflict]: ...


class LR0ParsingTable:
    """
    Table that contains all the transitions from state to state with a symbol.
    """

    def __init__(self, grammar: Grammar) -> None:
        self.rows: dict[LR0State, Row] = {}
        self._grammar = grammar
        self._initial_state: LR0State | None = None

    @classmethod
    def from_entries(cls, entries: Iterable[Entry], grammar: Grammar) -> Self:
        """
        Create a parsing table from the given entries.
        """
        table = cls(grammar)
        for entry in entries:
            table.add_entry(entry)
        return table

    @property
    def grammar(self) -> Grammar:
        """
        The grammar the table was created for.
        """
        return self._grammar

    @property
    def initial_state(self) -> LR0State:
        """
        The state the parser starts from, i.e. the state with number 1.
        Raises `ValueError` if the table has no entries from that state.
        """
        if self._initial_state is None:
            raise ValueError("parsing table has no initial state")

        return self._initial_state

    def get_actions(self, state: LR0State, symbol: Symbol) -> list[Action] | None:
        """
        Get the actions from state with given number with `symbol`.
        If there are no actions, returns None.
        """
        return self.rows.get(state, {}).get(symbol, None)

    def get(self, state: LR0State) -> Row | None:
        """
        Get the mapping of symbols to actions for the given state number.
        Returns None if the state is not found.
        """
        return self.rows.get(state, None)

    def add_entry(self, entry: Entry) -> None:
        """
        Adds an entry to the parsing table.
        """
        if entry.from_state.number == 1:
            self._initial_state = entry.from_state

        row = self.rows.setdefault(entry.from_state, {})
        actions = row.setdefault(entry.symbol, [])
        actions.append(entry.action)

    def pretty_str(self) -> str:
        """
        Returns a pretty-formatted string representation of the table.
        """
        return self._rules_pretty_str() + "\n\n" + self._table_pretty_str()

    def conflicts(self) -> list[Conflict]:
        """
        Retuns a list with all the conflicts in the parsing table.
        """
        conflicts = []
        for state, row in self.rows.items():
            for symbol, actions in row.items():
                if len(actions) > 1:
                    conflicts.append(Conflict(state, symbol, actions))

        return conflicts

    def _rules_pretty_str(self) -> str:
        rules = [f"{rule.number}. {rule}" for rule in self._grammar.rules]
        line = "-" * max(map(len, rules))

        return "\n".join(["GRAMMAR RULES", line, *rules, line])

    def _table_pretty_str(self) -> str:
        # ε is never an input token, so its column would always be empty.
        symbols = sorted(s for s in self._grammar.symbols if s != Symbol.null())

        header = ["", *map(str, symbols)]
        rows = [header]
        for state, row in sorted(self.rows.items(), key=lambda r: r[0].number or 0):
            cells = [str(state.number)]
            for symbol in symbols:
                actions = row.get(symbol, [])
                cells.append(",".join(map(str, actions)) if actions else "--")

            rows.append(cells)

        widths = [max(len(row[i]) for row in rows) for i in range(len(header))]
        lines = [
            "|" + "|".join(f"  {cell:<{w}}  " for cell, w in zip(row, widths)) + "|"
            for row in rows
        ]
        separator = "-" * len(lines[0])

        table = [self._header_str(), separator]
        for line in lines:
            table += [line, separator]

        return "\n".join(table) + "\n"

    def _header_str(self) -> str:
        return "LR0 PARSING TABLE"


class SLRParsingTable(LR0ParsingTable):
    """
    Table that contains all the transitions from state to state with a symbol.
    """

    def _header_str(self) -> str:
        return "SLR PARSING TABLE"


class LR1ParsingTable(LR0ParsingTable):
    """
    Table that contains all the transitions from state to state with a symbol.
    """

    def _header_str(self) -> str:
        return "LR1 PARSING TABLE"
