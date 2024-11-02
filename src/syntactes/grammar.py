from typing import Iterable

from syntactes import Rule, Token


class Grammar:
    """
    A grammar is a set of rules that describe a language.

    The only valid 'words' of the language are the given tokens.
    """

    def __init__(
        self, starting_rule: Rule, rules: Iterable[Rule], tokens: set[Token]
    ) -> None:
        """
        `starting_rule` should also be included in `rules`.
        """
        self.starting_rule = starting_rule
        self.rules = rules
        self.tokens = tokens
