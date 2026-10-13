"""
Loads grammars written in a yacc-like BNF, so that the tests for real languages
can state their grammars legibly.

    name
        : symbol symbol
        | symbol
        | %empty
        ;

Names defined on a left-hand side are non-terminals. Other symbols are
terminals, written either in uppercase (e.g. IDENTIFIER) or quoted (e.g. '(' or
'if'), and the quotes are not part of the token's symbol. `#` starts a comment.
"""

import re

from syntactes import Grammar, Rule, Symbol

_EMPTY = "%empty"


def grammar_from_bnf(bnf: str, start: str) -> Grammar:
    """
    Returns the grammar defined by the BNF, with the starting rule
    `<start> -> start $` numbered 0 and the other rules numbered in order.

    Raises `ValueError` if the BNF is malformed or uses an undefined lowercase
    name.
    """
    definitions = _parse(bnf)
    non_terminals = {lhs for lhs, _ in definitions}

    def symbol(word: str) -> Symbol:
        if word in non_terminals:
            return Symbol(word, False)

        if len(word) > 2 and word.startswith("'") and word.endswith("'"):
            return Symbol(word[1:-1], True)

        if not word.isupper():
            raise ValueError(f"Undefined non-terminal '{word}'.")

        return Symbol(word, True)

    starting_rule = Rule(0, Symbol("<start>", False), symbol(start), Symbol.eof())
    rules = [starting_rule]
    for lhs, alternatives in definitions:
        for alternative in alternatives:
            rhs = [symbol(word) for word in alternative]
            rules.append(Rule(len(rules), symbol(lhs), *rhs))

    symbols = {starting_rule.lhs, Symbol.eof()}
    for rule in rules:
        symbols.update(rule.rhs)

    return Grammar(starting_rule, rules, symbols)


def find_rule(grammar: Grammar, lhs: str, *rhs: str) -> Rule:
    """
    Returns the rule of the grammar with the given left-hand side and right-hand
    side, written as in the BNF. Raises `LookupError` if there is none.
    """
    for rule in grammar.rules:
        if rule.lhs.name != lhs:
            continue

        if [_word(symbol) for symbol in rule.rhs] == list(rhs):
            return rule

    raise LookupError(f"No rule {lhs} : {' '.join(rhs) or _EMPTY}")


def _word(symbol: Symbol) -> str:
    if symbol.is_terminal and not symbol.name.isupper():
        return f"'{symbol.name}'"

    return symbol.name


def _parse(bnf: str) -> list[tuple[str, list[list[str]]]]:
    words = re.sub(r"(?m)#.*$", "", bnf).split()
    definitions: list[tuple[str, list[list[str]]]] = []

    i = 0
    while i < len(words):
        if i + 1 >= len(words) or words[i + 1] != ":":
            raise ValueError(f"Expected ':' after '{words[i]}'.")

        lhs = words[i]
        alternatives: list[list[str]] = [[]]
        i += 2
        while True:
            if i >= len(words):
                raise ValueError(f"Definition of '{lhs}' is not terminated by ';'.")

            word = words[i]
            i += 1
            if word == ";":
                break

            if word == "|":
                alternatives.append([])
            elif word != _EMPTY:
                alternatives[-1].append(word)

        definitions.append((lhs, alternatives))

    return definitions
