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

On each reduction, the parser computes a value for the rule and pushes it as
the `value` of the left-hand side token, so the rule that later uses that token
receives it. The value comes from, in order:

1. the rule's callback, if one is registered;
2. the rule's [primitive](#primitives), if it has one;
3. the value of the rule's only token, if it has exactly one, so unit rules
   like `expr -> term` pass their value through;
4. otherwise, `None`.

When the parser accepts, it computes the starting rule's value the same way,
from its right-hand side tokens except the trailing `$`, and `parse()` returns
it. A starting rule with neither a callback nor a primitive returns the start
symbol's value.

To compute values yourself, register a callback for a rule with
`@parser.execute_on(rule)`. Registering a rule that's not in the parser's
grammar raises `ValueError`.

- The callback is called with one token per right-hand side symbol, in order,
  and its return value becomes the rule's value.
- Terminals carry the `value` they were created with, such as
  `Token("x", True, 42)`.
- An empty rule's callback is called with no arguments.
- A callback wins over the rule's primitive.
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

## Primitives

A rule's [primitive](grammars.md#primitives) computes its value when it has no
callback, so a grammar can evaluate its input without any callbacks:

- a binary operation, like `add(1,3)`, is called with the values of the tokens
  at its [operand positions](grammars.md#operands);
- a value type, like `int`, converts the value of the rule's single token;
- `None` gives `None`.

If a primitive raises, `parse()` raises a `PrimitiveError` naming the rule, with
the original exception as its `__cause__`.

```python
from syntactes import Grammar, Token
from syntactes.parser import LR1Parser, PrimitiveError

grammar = Grammar.from_text("""
add(1,3) % expr -> expr PLUS term
sub(1,3) % expr -> expr MINUS term
expr -> term
mul(1,3) % term -> term TIMES factor
term -> factor
int % factor -> NUMBER
factor -> LPAREN expr RPAREN
""")
parens = grammar.rules[-1]

parser = LR1Parser.from_grammar(grammar)


@parser.execute_on(parens)
def parenthesized(lparen, expr, rparen):
    # Three symbols and no primitive, so without a callback the value is None.
    return expr.value


KINDS = {"+": "PLUS", "-": "MINUS", "*": "TIMES", "(": "LPAREN", ")": "RPAREN"}


def lex(text):
    for word in text.split():
        yield Token(KINDS.get(word, "NUMBER"), True, word)
    yield Token.eof()


print(parser.parse(lex("2 * ( 7 - 2 - 1 ) + 3")))

try:
    parser.parse(lex("2 + x"))
except PrimitiveError as e:
    print(f"{e} ({e.__cause__!r})")
```

```
11
Primitive int of rule 'factor -> NUMBER' failed. (ValueError("invalid literal for int() with base 10: 'x'"))
```

`factor -> LPAREN expr RPAREN` has three symbols and no primitive, so it needs
a callback to keep the value of `expr`.

## Errors

`parse()` raises a `ParserError` from `syntactes.parser`:

- `UnexpectedTokenError` if a token has no action in the current state, or if
  tokens follow the `$` that completed the parse. Its `received_token` is the
  token, and its `expected_tokens` holds the terminals that would have been
  accepted, sorted.
- `NotAcceptedError` if the stream ends before the parser accepts, for example
  when the `$` is missing.
- `PrimitiveError` if a rule's [primitive](#primitives) raises. Its `rule` and
  `primitive` say which, and its `__cause__` is the original exception.

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
