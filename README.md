
[![image](https://img.shields.io/pypi/v/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![image](https://img.shields.io/pypi/l/syntactes.svg)](https://opensource.org/license/mit/)
[![image](https://img.shields.io/pypi/pyversions/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![Actions status](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml/badge.svg?branch=main)](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml?query=branch%3Amain)
---
# syntactes
A simpler Python parser generator.  
The name is derived from Greek _συντάκτης_ (/sin'daktis/) meaning editor/composer.

## Features
* Parsing table creation (LR0, SLR and LR1)
* Token parsing, with callbacks that compute values on each reduction

## Installation
```
> pip install syntactes
```

## Quick start

### Creating a parsing table
```py
from syntactes import Grammar, Rule, SLRGenerator, Token

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

Running the above example produces this output:
```
Parsing stream: 1 + 2 + 3 $

reducing by E -> T + E: 2 + 3
reducing by E -> T + E: 1 + 5
result: 6

Parsing stream: 1 + $

ParserError: Received token: $; expected one of: ['x']
```

## Callbacks

Callbacks are registered on a parser with `@parser.execute_on(rule)`. Registering
a rule that is not in the parser's grammar raises `ValueError`.

* On each reduction, the rule's callback is called with one token per right-hand
  side symbol, in order.
* The callback's return value becomes the `value` of the token pushed for the
  left-hand side, so the callback of an enclosing rule receives it. A rule
  without a callback pushes a token whose value is `None`.
* When the parser accepts, the starting rule's callback is called with its
  right-hand side tokens, except the trailing `$`. Its return value is returned
  by `parse()`. Without a callback for the starting rule, `parse()` returns
  `None`.
* Exceptions raised in callbacks propagate out of `parse()` unchanged.

## Errors

`parse()` raises a `syntactes.parser.ParserError`:

* `UnexpectedTokenError` if a token has no action in the current state, or if
  tokens follow the `$` that completed the parse. Its `expected_tokens` holds
  the terminals that would have been accepted, sorted.
* `NotAcceptedError` if the stream ends before the parser accepts.

## Grammars

`Grammar` raises `syntactes.GrammarError` (a `ValueError`) if:

* the starting rule is not in the rules, or doesn't end with `$`;
* `$` appears anywhere other than at the end of the starting rule;
* a rule's left-hand side is a terminal;
* a rule uses a symbol that is not in the tokens (`ε` is always allowed);
* a non-terminal has no rules;
* two rules have the same number.

An empty rule can be written as `Rule(n, A)` or `Rule(n, A, Token.null())`. Its
callback is called with no arguments.

## Conflicts

`table.conflicts()` lists the cells of a parsing table that hold more than one
action. When parsing, conflicts are resolved the way yacc resolves them: shift
wins over reduce, and between reduces the rule with the lowest number wins. For
example, with `E -> E + E`, `x + x + x` is parsed as `x + (x + x)`.
