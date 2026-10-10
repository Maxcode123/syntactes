# Parsing

## Creating a parser

There's a parser for each kind of [parsing table](parsing-tables.md):
`LR0Parser`, `SLRParser` and `LR1Parser`, all in `syntactes.parser`.
`from_grammar` generates the table and returns a parser for it:

```python
from syntactes.parser import SLRParser

parser = SLRParser.from_grammar(grammar)
```

If you already have a table, pass it to the constructor instead:
`SLRParser(table)`.

## Callbacks

On its own, a parser only checks that the tokens are valid. To compute
something, register a callback for a rule with `@parser.execute_on(rule)`.
Registering a rule that's not in the parser's grammar raises `ValueError`.

- On each reduction, the rule's callback is called with one token per
  right-hand side symbol, in order.
- The callback's return value becomes the `value` of the token pushed for the
  left-hand side, so the callback of an enclosing rule receives it. A rule
  without a callback pushes a token whose value is `None`.
- Terminals carry the `value` they were created with, such as
  `Token("x", True, 42)`.
- An empty rule's callback is called with no arguments.
- When the parser accepts, the starting rule's callback is called with its
  right-hand side tokens, except the trailing `$`. Its return value is returned
  by `parse()`. Without a callback for the starting rule, `parse()` returns
  `None`.
- Exceptions raised in callbacks propagate out of `parse()` unchanged.

`parse()` takes any iterable of tokens, a generator included, and expects `$`
(`Token.eof()`) as the last one.

```python
from syntactes import Grammar, Rule, Token
from syntactes.parser import ParserError, SLRParser

EOF = Token.eof()
S = Token("S", is_terminal=False)
E = Token("E", False)
T = Token("T", False)
x = Token("x", True)
PLUS = Token("+", True)

tokens = {EOF, S, E, T, x, PLUS}

# 0. S -> E $
# 1. E -> T + E
# 2. E -> T
# 3. T -> x
rule_1 = Rule(0, S, E, EOF)
rule_2 = Rule(1, E, T, PLUS, E)
rule_3 = Rule(2, E, T)
rule_4 = Rule(3, T, x)

rules = (rule_1, rule_2, rule_3, rule_4)

grammar = Grammar(rule_1, rules, tokens)

parser = SLRParser.from_grammar(grammar)


@parser.execute_on(rule_1)
def result(e):
    # The starting rule's callback gets every right-hand side token except $.
    # Its return value is returned by parse().
    return e.value


@parser.execute_on(rule_2)
def add(t, plus, e):
    # One token per right-hand side symbol, in order. A non-terminal's value is
    # whatever the callback of the rule that produced it returned.
    print(f"reducing by {rule_2}: {t.value} {plus} {e.value}")
    return t.value + e.value


@parser.execute_on(rule_3)
def term(t):
    return t.value


@parser.execute_on(rule_4)
def number(x_token):
    # Terminals carry the value they were created with.
    return x_token.value


def num(value):
    return Token("x", True, value)


print("Parsing stream: 1 + 2 + 3 $\n")
print("result:", parser.parse([num(1), PLUS, num(2), PLUS, num(3), EOF]))

print("\nParsing stream: 1 + $\n")
try:
    parser.parse([num(1), PLUS, EOF])
except ParserError as e:
    print("ParserError:", e)
```

```
Parsing stream: 1 + 2 + 3 $

reducing by E -> T + E: 2 + 3
reducing by E -> T + E: 1 + 5
result: 6

Parsing stream: 1 + $

ParserError: Received token: $; expected one of: ['x']
```

## Errors

`parse()` raises a `ParserError` from `syntactes.parser`:

- `UnexpectedTokenError` if a token has no action in the current state, or if
  tokens follow the `$` that completed the parse. Its `received_token` is the
  token, and its `expected_tokens` holds the terminals that would have been
  accepted, sorted.
- `NotAcceptedError` if the stream ends before the parser accepts, for example
  when the `$` is missing.

## Conflicts

A parser can use a table that has [conflicts](parsing-tables.md#conflicts). It
resolves them the way yacc does: shift wins over reduce, and between reduces
the rule with the lowest number wins.

For example, `expr -> expr PLUS expr` is ambiguous, and shifting makes `PLUS`
right-associative:

```python
from syntactes import Grammar, Token
from syntactes.parser import SLRParser

grammar = Grammar.from_text("""
expr -> expr PLUS expr
expr -> X
""")
start, add, x = grammar.rules

parser = SLRParser.from_grammar(grammar)


@parser.execute_on(start)
def result(expr):
    return expr.value


@parser.execute_on(add)
def on_add(left, plus, right):
    return f"({left.value} + {right.value})"


@parser.execute_on(x)
def on_x(x):
    return x.value


PLUS = Token("PLUS", True)
stream = [Token("X", True, "a"), PLUS, Token("X", True, "b"), PLUS, Token("X", True, "c")]
print(parser.parse([*stream, Token.eof()]))  # (a + (b + c))
```

To get left-associativity, write the grammar that way instead:
`expr -> expr PLUS X`.
