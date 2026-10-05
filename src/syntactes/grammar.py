from collections.abc import Iterable

from syntactes import Rule, Token


class GrammarError(ValueError):
    """
    The grammar is malformed.
    """


class Grammar:
    """
    A grammar is a set of rules that describe a language.

    The only valid 'words' of the language are the given tokens.
    """

    def __init__(
        self, starting_rule: Rule, rules: Iterable[Rule], tokens: set[Token]
    ) -> None:
        """
        `starting_rule` should also be included in `rules`, and end with the EOF
        token.

        Raises `GrammarError` if the grammar is malformed.
        """
        self.starting_rule = starting_rule
        self.rules = tuple(rules)
        self.tokens = tokens

        self._validate()

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
