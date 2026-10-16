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
`@parser.execute_on(rule)`. The rule can also be given
[as text](#rules-as-text). Registering a rule that's not in the parser's grammar
raises `ValueError`.

- The callback is called with one token per right-hand side symbol, in order,
  and its return value becomes the rule's value.
- Each token has a `symbol`, a [`location`](#locations) and a `value`. A
  terminal's token is the one from the stream, with the value it was read
  with, such as `Token(x, Location(0, 1, 1), 42)`. A non-terminal's token holds
  the value computed for its rule.
- An empty rule's callback is called with no arguments.
- A callback wins over the rule's primitive.
- Exceptions raised in callbacks propagate out of `parse()` unchanged.

`parse()` takes any iterable of `Token`s, a generator included. A token is a
terminal `Symbol` of the grammar, the [`Location`](#locations) it starts at,
and a `value`, which defaults to `None`. `parse()` expects a `$` token,
`Token(Symbol.eof(), location)`, as the last one.

```python
from syntactes import Grammar, Rule, Symbol, Token
from syntactes.parser import Location, SLRParser, UnexpectedTokenError

EOF = Symbol.eof()
S = Symbol("S", is_terminal=False)
E = Symbol("E", False)
T = Symbol("T", False)
x = Symbol("x", True)
PLUS = Symbol("+", True)

symbols = {EOF, S, E, T, x, PLUS}

# 0. S -> E $
# 1. E -> T + E
# 2. E -> T
# 3. T -> x
rule_1 = Rule(0, S, E, EOF)
rule_2 = Rule(1, E, T, PLUS, E)
rule_3 = Rule(2, E, T)
rule_4 = Rule(3, T, x)

rules = (rule_1, rule_2, rule_3, rule_4)

grammar = Grammar(rule_1, rules, symbols)

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
    # A non-terminal's token starts where its first token does.
    print(f"column {t.location.column}: reducing by {rule_2}: {t.value} + {e.value}")
    return t.value + e.value


@parser.execute_on(rule_3)
def term(t):
    return t.value


@parser.execute_on(rule_4)
def number(x_token):
    # Terminals carry the value they were created with.
    return x_token.value


def lex(text):
    # One token per character but spaces, located at its offset on line 1.
    for offset, char in enumerate(text):
        location = Location(offset, 1, offset + 1)
        if char == "+":
            yield Token(PLUS, location)
        elif char != " ":
            yield Token(x, location, int(char))
    yield Token(EOF, Location(len(text), 1, len(text) + 1))


print("Parsing: 1 + 2 + 3\n")
print("result:", parser.parse(lex("1 + 2 + 3")))

print("\nParsing: 1 +\n")
try:
    parser.parse(lex("1 +"))
except UnexpectedTokenError as e:
    print(f"column {e.received_token.location.column}: {e}")
```

```
Parsing: 1 + 2 + 3

column 5: reducing by E -> T + E: 2 + 3
column 1: reducing by E -> T + E: 1 + 5
result: 6

Parsing: 1 +

column 4: Received token: $; expected one of: ['x']
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
import re

from syntactes import Grammar, Symbol, Token
from syntactes.parser import Location, LR1Parser, PrimitiveError

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
    for match in re.finditer(r"\S+", text):
        location = Location(match.start(), 1, match.start() + 1)
        yield Token(Symbol(KINDS.get(match[0], "NUMBER"), True), location, match[0])
    yield Token(Symbol.eof(), Location(len(text), 1, len(text) + 1))


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

## Rules as text

`execute_on` also takes a rule's text, as `str(rule)` prints it, and looks it up
in the parser's grammar, so you don't need to hold on to the `Rule`:

- Symbols are separated by whitespace and matched by name, as in
  `"E -> T + E"`.
- An empty rule is `"A -> ε"` or `"A ->"`.
- The starting rule ends with `$`. A `Grammar.from_text` grammar's is
  `"<start> -> expr $"`, where `expr` is the first rule's left-hand side.
- The text can start with the rule's [primitive](grammars.md#primitives), as in
  `Grammar.from_text`. It must then be the rule's primitive in the grammar, and
  its operands, if you give any, the rule's operands. `"add % expr -> expr PLUS
  term"` matches any operands.

Text that doesn't name exactly one rule of the grammar, or gives a primitive
the rule doesn't have, raises `ValueError`. If two symbols share a name, as a
terminal and a non-terminal, pass the `Rule` instead.

```python
from syntactes import Grammar, Symbol, Token
from syntactes.parser import Location, LR1Parser

grammar = Grammar.from_text("""
add(1,3) % expr -> expr PLUS term
expr -> term
int % term -> NUMBER
""")

parser = LR1Parser.from_grammar(grammar)


@parser.execute_on("<start> -> expr $")
def result(expr):
    return f"= {expr.value}"


@parser.execute_on("int % term -> NUMBER")
def tens(number):
    # The prefix is checked against the grammar, but the callback still wins
    # over the primitive.
    return int(number.value) * 10


NUMBER, PLUS = Symbol("NUMBER", True), Symbol("PLUS", True)
stream = [
    Token(NUMBER, Location(0, 1, 1), "1"),
    Token(PLUS, Location(2, 1, 3)),
    Token(NUMBER, Location(4, 1, 5), "2"),
    Token(Symbol.eof(), Location(5, 1, 6)),
]
print(parser.parse(stream))

for text in ["expr -> term term", "sub % expr -> expr PLUS term"]:
    try:
        parser.execute_on(text)
    except ValueError as e:
        print(e)
```

```
= 30
Rule 'expr -> term term' is not in the parser's grammar.
Rule 'expr -> expr PLUS term' has primitive 'add', not 'sub'.
```

## Locations

Every token has a `location`, a `Location(offset, line, column)` saying where it
starts in the source text. The offset is 0-based, and the line and column are
1-based. Your lexer gives each terminal's token its location, and the parser
gives each non-terminal's token the location of its first right-hand side
token, so a callback can tell where its rule's text starts. An empty rule has no
tokens, so its token gets the location of the token that follows it.

If your lexer has a location type of its own, `Location.from_object` builds a
`Location` from any object with `offset`, `line` and `column` attributes, like
the locations of [lectes](https://maximosnikiforakis.gr/lectes/) tokens, or from
a mapping with those keys. It raises `LocationObjectError`, a `ParserError`, if
one is missing or isn't an integer, with the conversion's exception as its
`__cause__`:

```python
from syntactes.parser import Location, LocationObjectError

print(Location.from_object({"offset": 4, "line": 2, "column": 3}))

try:
    Location.from_object({"offset": 4, "line": "two", "column": 3})
except LocationObjectError as e:
    print(f"{e} ({e.__cause__!r})")
```

```
Location(offset=4, line=2, column=3)
cannot create Location object from {'offset': 4, 'line': 'two', 'column': 3}, 'line' cannot be converted to an integer (ValueError("invalid literal for int() with base 10: 'two'"))
```

## Errors

`parse()` raises a `ParserError` from `syntactes.parser`:

- `UnexpectedTokenError` if a token has no action in the current state, or if
  tokens follow the `$` that completed the parse. Its `received_token` is the
  token, and its `expected_symbols` holds the terminals that would have been
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
from syntactes import Grammar, Symbol, Token
from syntactes.parser import Location, SLRParser

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


PLUS, X = Symbol("PLUS", True), Symbol("X", True)


def lex(text):
    for offset, char in enumerate(text):
        location = Location(offset, 1, offset + 1)
        if char == "+":
            yield Token(PLUS, location)
        elif char != " ":
            yield Token(X, location, char)
    yield Token(Symbol.eof(), Location(len(text), 1, len(text) + 1))


print(parser.parse(lex("a + b + c")))  # (a + (b + c))
```

To get left-associativity, write the grammar that way instead:
`expr -> expr PLUS X`.
