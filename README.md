
[![image](https://img.shields.io/pypi/v/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![image](https://img.shields.io/pypi/l/syntactes.svg)](https://opensource.org/license/mit/)
[![image](https://img.shields.io/pypi/pyversions/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![Actions status](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml/badge.svg?branch=main)](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml?query=branch%3Amain)
---
# syntactes
Python parser generator

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
rule_4 = Rule(4, T, x)

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
|     |  $   |  +   |  E   |  S   |  T   |  x  |
-------------------------------------------------
|  1  |  --  |  --  |  s4  |  --  |  s2  |  s3 |
-------------------------------------------------
|  2  |  r2  |  s5  |  --  |  --  |  --  |  -- |
-------------------------------------------------
|  3  |  r4  |  r4  |  --  |  --  |  --  |  -- |
-------------------------------------------------
|  4  |  a  |  --  |  --  |  --  |  --  |  -- |
------------------------------------------------
|  5  |  --  |  --  |  s6  |  --  |  s2  |  s3 |
-------------------------------------------------
|  6  |  r1  |  --  |  --  |  --  |  --  |  -- |
-------------------------------------------------
```

### Parsing

```py
from syntactes import Grammar, Rule, Token
from syntactes.parser import ParserError, SLRParser, execute_on

EOF = Token.eof()
S = Token("S", is_terminal=False)
E = Token("E", False)
T = Token("T", False)
x = Token("x", True, 1)  # value of token is 1
PLUS = Token("+", True)

tokens = {EOF, S, E, T, x, PLUS}

# 0. S -> E $
# 1. E -> T + E
# 2. E -> T
# 3. T -> x
rule_1 = Rule(0, S, E, EOF)
rule_2 = Rule(1, E, T, PLUS, E)
rule_3 = Rule(2, E, T)
rule_4 = Rule(4, T, x)

rules = (rule_1, rule_2, rule_3, rule_4)

grammar = Grammar(rule_1, rules, tokens)

parser = SLRParser.from_grammar(grammar)


@execute_on(rule_4)
def push_value(x_token):
    # Add and argument for every token on the right-hand side of the rule.
    print(
        f"received token {x_token} with value: {x_token.value}, reducing by rule: {rule_4}"
    )


@execute_on(rule_2)
def add(left, plus, right):
    print(f"received tokens {left}, {plus}, {right}, reducing by rule: {rule_2}")


print("Parsing stream: x + x + x $\n")
parser.parse([x, PLUS, x, PLUS, x, EOF])

print("\nParsing stream: x + $\n")
try:
    parser.parse([x, PLUS, EOF])
except ParserError as e:
    print("ParserError:", e)
```

Running the above example produces this output:
```
Parsing stream: x + x + x $

received token x with value: 1, reducing by rule: T -> x
received token x with value: 1, reducing by rule: T -> x
received token x with value: 1, reducing by rule: T -> x
received tokens E, +, T, reducing by rule: E -> T + E
received tokens E, +, T, reducing by rule: E -> T + E

Parsing stream: x + $

received token x with value: 1, reducing by rule: T -> x
ParserError: Received token: $; expected one of: ['x', 'T', 'E']
```
