# Parsing tables

A parsing table tells an LR parser what to do in each state for each input
token: shift the token, reduce by a rule, or accept. syntactes has a generator
for each kind of table:

| Generator | Table | Reduces on |
|---|---|---|
| `LR0Generator` | `LR0ParsingTable` | every token |
| `SLRGenerator` | `SLRParsingTable` | the tokens that can follow the rule's left-hand side (its FOLLOW set) |
| `LR1Generator` | `LR1ParsingTable` | the tokens that can follow the rule in that state (its lookaheads) |

Each one handles more grammars than the one before it, and LR1 tables have the
most states. If you only want a parser, you don't have to build the table
yourself: see [Parsing](parsing.md).

## Generating a table

Pass the grammar to a generator and call `generate()`. `pretty_str()` prints the
rules and the table:

```python
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

`sN` shifts and goes to state `N`, `rN` reduces by rule `N`, and `a` accepts.
For non-terminal columns, `sN` is the state to go to after a reduction.
States are numbered breadth-first from 1, and the same grammar always gives
the same table.

## Conflicts

A cell with more than one action is a conflict. `conflicts()` lists them. Each
`Conflict` has the `state`, the `token`, the `actions` and a `conflict_type`:
`SHIFT_REDUCE`, `REDUCE_REDUCE` or `SHIFT_SHIFT`.

The grammar above has a conflict as an LR0 table, but not as an SLR table. In
state 3, LR0 reduces by `E -> T` on every token, `+` included, while SLR only
reduces on the tokens that can follow `E`:

```python
from syntactes import Grammar, LR0Generator, SLRGenerator

grammar = Grammar.from_text("""
expr -> term PLUS expr
expr -> term
term -> NUMBER
""")

for generator_cls in (LR0Generator, SLRGenerator):
    table = generator_cls(grammar).generate()
    print(generator_cls.__name__, len(table.conflicts()), "conflicts")

for conflict in LR0Generator(grammar).generate().conflicts():
    actions = [str(action) for action in conflict.actions]
    print(conflict.conflict_type.value, conflict.state.number, conflict.token, actions)
```

```
LR0Generator 1 conflicts
SLRGenerator 0 conflicts
shift/reduce 3 PLUS ['s5', 'r2']
```

`conflict.pretty_str()` describes a conflict in full, with the items of its
state and of the state a shift goes to.

Some grammars need LR1. In this classic one, SLR can't tell when to reduce
`r -> l`, because `EQUALS` can follow `r` somewhere in the grammar, even though
it can't in that state:

```python
from syntactes import Grammar, LR1Generator, SLRGenerator

grammar = Grammar.from_text("""
s -> l EQUALS r
s -> r
l -> STAR r
l -> ID
r -> l
""")

for generator_cls in (SLRGenerator, LR1Generator):
    table = generator_cls(grammar).generate()
    print(generator_cls.__name__, [c.conflict_type.value for c in table.conflicts()])
```

```
SLRGenerator ['shift/reduce']
LR1Generator []
```

A table with conflicts can still be used to parse. See
[how the parser resolves them](parsing.md#conflicts).
