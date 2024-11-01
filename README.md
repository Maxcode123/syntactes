
[![image](https://img.shields.io/pypi/v/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![image](https://img.shields.io/pypi/l/syntactes.svg)](https://opensource.org/license/mit/)
[![image](https://img.shields.io/pypi/pyversions/syntactes.svg)](https://pypi.python.org/pypi/syntactes)
[![Actions status](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml/badge.svg?branch=main)](https://github.com/Maxcode123/syntactes/actions/workflows/test-package.yml?query=branch%3Amain)
---
# syntactes
Python parser generator

## Quick start
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

LR0 PARSING TABLE
-------------------------------------------------
|     |  $   |  +   |  E   |  S   |  T   |  x  |
-------------------------------------------------
|  1  |  --  |  --  |  s3  |  --  |  s4  |  s2 |
-------------------------------------------------
|  2  |  r4  |  r4  |  --  |  --  |  --  |  -- |
-------------------------------------------------
|  3  |  a  |  --  |  --  |  --  |  --  |  -- |
------------------------------------------------
|  4  |  r2  |  s5  |  --  |  --  |  --  |  -- |
-------------------------------------------------
|  5  |  --  |  --  |  s6  |  --  |  s4  |  s2 |
-------------------------------------------------
|  6  |  r1  |  --  |  --  |  --  |  --  |  -- |
-------------------------------------------------
```
