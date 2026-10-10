"""
Parser for the grammar text format read by `Grammar.from_text`.

One rule per line: a left-hand side, `->`, then the right-hand side symbols,
separated by whitespace. Blank lines and lines starting with `#` are ignored.
Names that appear on a left-hand side are non-terminals; every other symbol is a
terminal. An empty right-hand side, or a lone `ε`, is an empty rule.
"""

import re
from dataclasses import dataclass, field

from syntactes import Rule, Token
from syntactes.primitive import (
    Primitive,
    primitives,
)

START_SYMBOL = "<start>"

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ARROW = "->"
_PERCENT = "%"


@dataclass
class _Line:
    number: int
    primitive: str | None
    lhs: str
    rhs: list[str]


@dataclass
class ParsedText:
    rules: list[Rule] = field(default_factory=list)
    primitives: dict[Rule, Primitive] = field(default_factory=dict)
    errors: list[tuple[int | None, str]] = field(default_factory=list)
    warnings: list[tuple[int, str]] = field(default_factory=list)


def parse(text: str) -> ParsedText:
    """
    Parse grammar text, reporting every problem rather than stopping at the
    first one. Warnings are only computed once there are no errors.
    """
    result = ParsedText()
    lines = _lines(text, result.errors)

    if not lines and not result.errors:
        result.errors.append((None, "grammar has no rules"))

    if result.errors:
        return result

    non_terminals = {line.lhs for line in lines}

    def token(symbol: str) -> Token:
        return Token(symbol, symbol not in non_terminals)

    def primitive(raw: str | None) -> Primitive | None:
        if not raw or len(raw) == 0:
            return None

        for prim in primitives():
            if raw == prim.string():
                return prim

        return None

    start = Token(lines[0].lhs, False)
    result.rules.append(Rule(0, Token(START_SYMBOL, False), start, Token.eof()))
    for number, line in enumerate(lines, start=1):
        prim = primitive(line.primitive)
        rule = Rule(number, token(line.lhs), *map(token, line.rhs))
        result.rules.append(rule)
        if prim is not None:
            result.primitives[rule] = prim

    result.warnings = _warnings(lines, result.rules[1:], start)
    return result


def _lines(text: str, errors: list[tuple[int | None, str]]) -> list[_Line]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[_Line] = []
    seen: dict[tuple[str, tuple[str, ...]], int] = {}

    for number, raw in enumerate(text.split("\n"), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        left, arrow, rest = stripped.partition(_ARROW)
        primitive, percent, lhs = left.partition(_PERCENT)

        if not lhs:
            lhs = primitive.strip()
            primitive = None
        else:
            primitive = primitive.strip()
            lhs = lhs.strip()

        rhs = rest.split()

        error = _line_error(primitive, percent, lhs, arrow, rhs)
        if error is not None:
            errors.append((number, error))
            continue

        if rhs == [Token.null().symbol]:
            rhs = []

        key = (lhs, tuple(rhs))
        if key in seen:
            errors.append((number, f"duplicate of the rule on line {seen[key]}"))
            continue

        seen[key] = number
        lines.append(_Line(number, primitive, lhs, rhs))

    return lines


def _line_error(
    primitive: str | None, percent: str, lhs: str, arrow: str, rhs: list[str]
) -> str | None:
    if not arrow:
        return f"expected 'lhs {_ARROW} symbols'"

    if not lhs:
        return "rule has no left-hand side"

    if not _NAME.fullmatch(lhs):
        return f"invalid left-hand side {lhs!r}"

    if primitive and not lhs:
        return f"expected 'primitive {_PERCENT} lhs {_ARROW} symbols'"

    names = [p.string() for p in primitives()]
    if primitive and primitive not in names:
        return f"invalid primitive {primitive} expected one of {', '.join(names)}"

    if percent and not primitive:
        return f"expected 'primitive {_PERCENT} lhs {_ARROW} symbols'"

    null, eof = Token.null().symbol, Token.eof().symbol
    for symbol in rhs:
        if symbol == eof:
            return f"'{eof}' is reserved for the end of the input"

        if symbol == null:
            if len(rhs) > 1:
                return f"{null} can only stand alone"
            continue

        if not _NAME.fullmatch(symbol):
            return f"invalid symbol {symbol!r}"

    return None


def _warnings(
    lines: list[_Line], rules: list[Rule], start: Token
) -> list[tuple[int, str]]:
    first_lines: dict[Token, int] = {}
    for line, rule in zip(lines, rules, strict=True):
        first_lines.setdefault(rule.lhs, line.number)

    reachable = _reachable(rules, start)
    productive = _productive(rules)

    found: list[tuple[int, str]] = []
    for symbol, number in first_lines.items():
        if symbol not in reachable:
            message = (
                f"non-terminal '{symbol}' can't be reached from the start "
                f"symbol '{start}'"
            )
            found.append((number, message))

        if symbol not in productive:
            found.append(
                (number, f"non-terminal '{symbol}' can't derive a string of terminals")
            )

    return found


def _reachable(rules: list[Rule], start: Token) -> set[Token]:
    reachable = {start}
    pending = [start]
    while pending:
        symbol = pending.pop()
        for rule in rules:
            if rule.lhs != symbol:
                continue

            for rhs_symbol in rule.rhs:
                if not rhs_symbol.is_terminal and rhs_symbol not in reachable:
                    reachable.add(rhs_symbol)
                    pending.append(rhs_symbol)

    return reachable


def _productive(rules: list[Rule]) -> set[Token]:
    productive: set[Token] = set()
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule.lhs in productive:
                continue

            if all(s.is_terminal or s in productive for s in rule.rhs):
                productive.add(rule.lhs)
                changed = True

    return productive
