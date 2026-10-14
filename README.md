
[![image](https://img.shields.io/pypi/v/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![image](https://img.shields.io/pypi/l/syntactes.svg)](https://opensource.org/license/mit/)
[![image](https://img.shields.io/pypi/pyversions/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![Actions status](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml/badge.svg?branch=main)](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml?query=branch%3Amain)

<p align="center">
  <a href="https://maximosnikiforakis.gr/syntactes/"><b>Documentation</b></a>
  &nbsp;·&nbsp;
  <a href="https://pypi.org/project/syntactes/"><b>PyPI</b></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/Maxcode123/syntactes"><b>GitHub</b></a>
</p>

---
# syntactes
A simpler Python parser generator.  
The name is derived from Greek _συντάκτης_ (/sin'daktis/) meaning editor/composer.

## Features
* Parsing table creation (LR0, SLR and LR1)
* Token parsing, with callbacks or grammar primitives (`add(1,3) % expr -> expr PLUS expr`)
  that compute values on each reduction
* Grammars written as text, one rule per line

## Installation
```
> pip install syntactes
```

## Quick start

### Creating a parsing table
```py
from syntactes import Grammar, Rule, SLRGenerator, Symbol

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

generator = SLRGenerator(grammar)

parsing_table = generator.generate()

print(parsing_table.pretty_str())
```

Running the above example produces this output:
```
GRAMMAR RULES
-------------
0. S -> E $
1. E -> T + E
2. E -> T
3. T -> x
-------------

SLR PARSING TABLE
-------------------------------------------------
|     |  $   |  +   |  E   |  S   |  T   |  x   |
-------------------------------------------------
|  1  |  --  |  --  |  s2  |  --  |  s3  |  s4  |
-------------------------------------------------
|  2  |  a   |  --  |  --  |  --  |  --  |  --  |
-------------------------------------------------
|  3  |  r2  |  s5  |  --  |  --  |  --  |  --  |
-------------------------------------------------
|  4  |  r3  |  r3  |  --  |  --  |  --  |  --  |
-------------------------------------------------
|  5  |  --  |  --  |  s6  |  --  |  s3  |  s4  |
-------------------------------------------------
|  6  |  r1  |  --  |  --  |  --  |  --  |  --  |
-------------------------------------------------
```

### Parsing

```py
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

Running the above example produces this output:
```
Parsing: 1 + 2 + 3

column 5: reducing by E -> T + E: 2 + 3
column 1: reducing by E -> T + E: 1 + 5
result: 6

Parsing: 1 +

column 4: Received token: $; expected one of: ['x']
```

## Learn more

The [documentation](https://maximosnikiforakis.gr/syntactes/) covers the rest:

* [Grammars](https://maximosnikiforakis.gr/syntactes/grammars/): writing grammars as text with
  `Grammar.from_text`, building them from `Symbol`s and `Rule`s, empty rules,
  and the errors and warnings for malformed grammars.
* [Parsing tables](https://maximosnikiforakis.gr/syntactes/parsing-tables/): the LR0, SLR and LR1
  generators, reading `pretty_str()`, and finding conflicts.
* [Parsing](https://maximosnikiforakis.gr/syntactes/parsing/): callbacks, primitives, `ParserError`s, and how the
  parser resolves conflicts.
* [API reference](https://maximosnikiforakis.gr/syntactes/syntactes/).
