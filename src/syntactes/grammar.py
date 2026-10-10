import warnings
from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import Self

from syntactes import Rule, Token, _text
from syntactes.primitive import NoneType, Primitive, _is_binary, primitives


class GrammarError(ValueError):
    """
    The grammar is malformed.

    Every error found is available as `problems`, a list of `(line, message)`
    pairs. `line` is the 1-based line of the text passed to `Grammar.from_text`,
    or None when the problem isn't tied to a line.
    """

    def __init__(
        self, message: str, problems: list[tuple[int | None, str]] | None = None
    ) -> None:
        super().__init__(message)
        self.problems = [(None, message)] if problems is None else problems

    @classmethod
    def from_problems(cls, problems: list[tuple[int | None, str]]) -> Self:
        message = "\n".join(
            text if line is None else f"line {line}: {text}" for line, text in problems
        )
        return cls(message, problems)


class GrammarWarning(UserWarning):
    """
    The text passed to `Grammar.from_text` is a valid grammar, but probably not
    what was intended.

    The 1-based line is available as `line` and the text as `message`.
    """

    def __init__(self, line: int, message: str) -> None:
        super().__init__(f"line {line}: {message}")
        self.line = line
        self.message = message


class Grammar:
    """
    A grammar is a set of rules that describe a language.

    The only valid 'words' of the language are the given tokens.
    """

    def __init__(
        self,
        starting_rule: Rule,
        rules: Iterable[Rule],
        tokens: set[Token],
        *,
        primitives: Mapping[Rule, Primitive] | None = None,
        operands: Mapping[Rule, tuple[int, int]] | None = None,
    ) -> None:
        """
        `starting_rule` should also be included in `rules`, and end with the EOF
        token.

        `primitives` maps some of the rules to a primitive from
        `syntactes.primitive`. A rule is matched by its symbols, not its number.

        `operands` maps rules whose primitive is a binary operation to the
        1-based positions of their two operands among the right-hand side
        symbols, e.g. `(1, 3)` for `expr -> expr PLUS expr`. A binary operation
        without an entry gets its first and last symbols.

        Raises `GrammarError` if the grammar is malformed.
        """
        self.starting_rule = starting_rule
        self.rules = tuple(rules)
        self.tokens = tokens
        self._primitives = dict(primitives or {})
        self._operands = dict(operands or {})

        self._validate()

    @property
    def primitives(self) -> Mapping[Rule, Primitive]:
        """
        The rules' primitives, from `syntactes.primitive`. It's read-only, and
        rules without a primitive aren't in it.
        """
        # Stored as a dict and wrapped on access, because a mappingproxy can't
        # be pickled or deep-copied.
        return MappingProxyType(self._primitives)

    @property
    def operands(self) -> Mapping[Rule, tuple[int, int]]:
        """
        The 1-based positions of the two operands of each rule whose primitive is
        a binary operation, e.g. `(1, 3)` for `add(1,3) % expr -> expr PLUS expr`.
        Every such rule is in it, and no other. It's read-only.
        """
        return MappingProxyType(self._operands)

    @classmethod
    def from_text(cls, text: str) -> Self:
        """
        Create a grammar from text with one rule per line:

            expr -> expr PLUS term
            expr -> term
            term -> NUMBER

        Names on a left-hand side are non-terminals, and every other symbol is a
        terminal. An empty right-hand side, or a lone `ε`, is an empty rule.
        Blank lines and lines starting with `#` are ignored.

        A rule can start with a primitive and `%`, as in
        `int % expr -> NUMBER`. It's stored in `primitives`. A binary operation
        can name its operands' positions, as in `add(1,3) % expr -> expr PLUS
        expr`, which are stored in `operands`.

        The first rule's left-hand side is the start symbol: the starting rule
        `<start> -> expr $` is added as rule 0, and the rules of the text are
        numbered from 1 in order.

        Raises `GrammarError` with every problem found, each with its line.
        Warns with `GrammarWarning` about non-terminals that can't be reached
        from the start symbol or can't derive a string of terminals.
        """
        parsed = _text.parse(text)
        if parsed.errors:
            raise GrammarError.from_problems(parsed.errors)

        for line, message in parsed.warnings:
            warnings.warn(GrammarWarning(line, message), stacklevel=2)

        tokens = {Token.eof()}
        for rule in parsed.rules:
            tokens.add(rule.lhs)
            tokens.update(rule.rhs)

        return cls(
            parsed.rules[0],
            parsed.rules,
            tokens,
            primitives=parsed.primitives,
            operands=parsed.operands,
        )

    def terminals(self) -> set[Token]:
        """
        Returns the terminals of the grammar, except `$` and `ε`.
        """
        special = {Token.eof(), Token.null()}
        return {t for t in self.tokens if t.is_terminal and t not in special}

    def _validate(self) -> None:
        EOF, NULL = Token.eof(), Token.null()

        if self.starting_rule not in self.rules:
            raise GrammarError(
                f"Starting rule '{self.starting_rule}' is not in the rules."
            )

        if self.starting_rule.rhs[-1:] != (EOF,):
            raise GrammarError(
                f"Starting rule '{self.starting_rule}' does not end with {EOF}."
            )

        numbers: set[int] = set()
        lhs_symbols = {rule.lhs for rule in self.rules}

        for rule in self.rules:
            if rule.number in numbers:
                raise GrammarError(f"Rule number {rule.number} is used twice.")
            numbers.add(rule.number)

            if rule.lhs.is_terminal:
                raise GrammarError(f"Rule '{rule}' has a terminal left-hand side.")

            eof_count = rule.rhs.count(EOF)
            if eof_count > 1 or (eof_count == 1 and rule != self.starting_rule):
                raise GrammarError(
                    f"Rule '{rule}' uses {EOF}, which may only end the starting rule."
                )

            for symbol in (rule.lhs, *rule.rhs):
                if symbol == NULL:
                    continue

                if symbol not in self.tokens:
                    raise GrammarError(
                        f"Symbol '{symbol}' of rule '{rule}' is not in the tokens."
                    )

                if not symbol.is_terminal and symbol not in lhs_symbols:
                    raise GrammarError(f"Non-terminal '{symbol}' has no rules.")

        valid = primitives()
        for rule, primitive in self._primitives.items():
            if rule not in self.rules:
                raise GrammarError(
                    f"Primitive given for rule '{rule}', which is not in the rules."
                )

            if primitive not in valid:
                raise GrammarError(
                    f"Primitive {primitive!r} of rule '{rule}' is not one of "
                    "syntactes.primitive.primitives()."
                )

        for rule in self._operands:
            if rule not in self.rules:
                raise GrammarError(
                    f"Operands given for rule '{rule}', which is not in the rules."
                )

            primitive = self._primitives.get(rule)
            if primitive is None or not _is_binary(primitive):
                raise GrammarError(
                    f"Operands given for rule '{rule}', whose primitive isn't a "
                    "binary operation."
                )

        for rule, primitive in self._primitives.items():
            count = self._symbol_count(rule)
            if not _is_binary(primitive):
                if primitive is not NoneType and count != 1:
                    raise GrammarError(
                        f"Rule '{rule}' needs exactly 1 symbol for its primitive "
                        f"{primitive.string()}."
                    )
                continue

            if count < 2:
                raise GrammarError(
                    f"Rule '{rule}' needs at least 2 symbols for its primitive "
                    f"{primitive.string()}."
                )

            left, right = self._operands.setdefault(rule, (1, count))
            for position in (left, right):
                if not 1 <= position <= count:
                    raise GrammarError(
                        f"Operand position {position} of rule '{rule}' is out of "
                        f"range 1-{count}."
                    )

            if left == right:
                raise GrammarError(f"Operand positions of rule '{rule}' must differ.")

    def _symbol_count(self, rule: Rule) -> int:
        """
        The number of tokens a primitive of `rule` gets: none for an empty rule,
        and the starting rule's trailing EOF doesn't count.
        """
        if rule.is_empty():
            return 0

        if rule == self.starting_rule:
            return rule.rhs_len - 1

        return rule.rhs_len
