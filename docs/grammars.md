# Grammars

A grammar is a set of rules that describe a language. Each rule breaks a
non-terminal symbol down into other symbols. You can write the grammar as text,
or build it from `Token` and `Rule` objects.

## Writing a grammar as text

`Grammar.from_text` builds a grammar from text with one rule per line:

```python
from syntactes import Grammar

grammar = Grammar.from_text("""
# Sums of numbers
expr -> expr PLUS NUMBER
expr -> NUMBER
""")

for rule in grammar.rules:
    print(f"{rule.number}. {rule}")
print(sorted(map(str, grammar.terminals())))
```

```
0. <start> -> expr $
1. expr -> expr PLUS NUMBER
2. expr -> NUMBER
['NUMBER', 'PLUS']
```

- A rule is a left-hand side, `->`, then the right-hand side symbols separated
  by whitespace. Names match `[A-Za-z_][A-Za-z0-9_]*`.
- Names that appear on a left-hand side are non-terminals. Every other symbol
  is a terminal. `grammar.terminals()` returns them, without `$` and `ε`.
- An empty right-hand side (`items ->`), or a lone `ε` (`items -> ε`), is an
  empty rule.
- Blank lines and lines starting with `#` are ignored.
- The first rule's left-hand side is the start symbol. The starting rule
  `<start> -> expr $` is added as rule 0, and the rules of the text are
  numbered from 1 in order, so rule `n` is the `n`-th rule line.

Since the rules are numbered in order, you can unpack `grammar.rules` to get
hold of them, for example to [register callbacks](parsing.md#callbacks):

```python
start, add, number = grammar.rules
```

### Primitives

A rule can start with a primitive and `%`: `int % expr -> NUMBER`. The
primitive is stored in `grammar.primitives`, a read-only mapping from rules to
primitives. Rules without one, the starting rule included, aren't in it.

Each primitive is one of the classes in `syntactes.primitive`. There are two
kinds. A value type converts one value when it's called:

| Text    | Class      | Call                                        |
| ------- | ---------- | ------------------------------------------- |
| `int`   | `Integer`  | `Integer("42")` is `42`                     |
| `float` | `Float`    | `Float("4.2")` is `4.2`                     |
| `str`   | `String`   | `String(42)` is `"42"`                      |
| `None`  | `NoneType` | `NoneType(x)` is always `None`              |
| `bool`  | `Boolean`  | `True` for `"1"` or `"true"`, else `False`  |

A value type's rule must have exactly one symbol, the one it converts, as in
`int % expr -> NUMBER`. `None` ignores its input, so it can tag any rule. For
the starting rule, the trailing `$` doesn't count.

A binary operation takes two operands when it's called, and returns the
result:

| Text  | Class                        | Call returns     |
| ----- | ---------------------------- | ---------------- |
| `add` | `Addition`                   | `left + right`   |
| `sub` | `Subtraction`                | `left - right`   |
| `mul` | `Multiplication`             | `left * right`   |
| `div` | `Division`                   | `left / right`   |
| `pow` | `Exponentiation`             | `left ** right`  |
| `lt`  | `LowerThanComparison`        | `left < right`   |
| `le`  | `LowerEqualThanComparison`   | `left <= right`  |
| `gt`  | `GreaterThanComparison`      | `left > right`   |
| `ge`  | `GreaterEqualThanComparison` | `left >= right`  |
| `eq`  | `EqualityComparison`         | `left == right`  |
| `ne`  | `InequalityComparison`       | `left != right`  |

```python
from syntactes import Grammar
from syntactes.primitive import Addition, Boolean, Integer, LowerThanComparison

grammar = Grammar.from_text("""
None % stmt -> PRINT expr
bool % stmt -> TRUE
add % expr -> expr PLUS NUMBER
int % expr -> NUMBER
""")

for rule in grammar.rules:
    primitive = grammar.primitives.get(rule)
    name = primitive.__name__ if primitive else "-"
    print(f"{rule.number}. {rule}  [{name}]")

print(repr(Integer("42")), repr(Boolean("true")))
print(Addition(1, 2), LowerThanComparison(1, 2))
```

```
0. <start> -> stmt $  [-]
1. stmt -> PRINT expr  [NoneType]
2. stmt -> TRUE  [Boolean]
3. expr -> expr PLUS NUMBER  [Addition]
4. expr -> NUMBER  [Integer]
42 True
3 True
```

Every primitive's `string()` method returns the name used in the text.
`syntactes.primitive.primitives()` returns all of them, in the order of the
tables above. The primitive isn't part of the rule, so `str(rule)` doesn't
print it.

Rules are compared by their symbols, so `int % expr -> NUMBER` and
`float % expr -> NUMBER` in the same grammar are duplicates.

#### Operands

A binary operation can say which right-hand side symbols are its operands, by
their 1-based positions: `add(1,3) % expr -> expr PLUS expr` adds the first and
third symbols. The order counts, so `sub(4,2)` is the fourth symbol minus the
second. Without positions, the operands are the first and last symbols. The
positions are stored in `grammar.operands`, a read-only mapping that holds every
rule whose primitive is a binary operation, and no other rule.

```python
grammar = Grammar.from_text("""
add(1,3) % expr -> expr PLUS expr
sub(4,2) % expr -> SUBTRACT expr FROM expr
mul % expr -> expr TIMES expr
expr -> NUMBER
""")

for rule, (left, right) in grammar.operands.items():
    print(f"{rule}  [{grammar.primitives[rule].__name__} ${left} ${right}]")
```

```
expr -> expr PLUS expr  [Addition $1 $3]
expr -> SUBTRACT expr FROM expr  [Subtraction $4 $2]
expr -> expr TIMES expr  [Multiplication $1 $3]
```

A binary operation's rule needs at least 2 symbols, and its two positions must
be different and between 1 and the number of symbols. Value types don't take
positions.

### Errors

`from_text` reports every problem at once. It raises a `GrammarError`, whose
`problems` list holds `(line, message)` pairs. `line` is 1-based, or `None` for
a problem that isn't tied to a line, such as an empty grammar.

```python
from syntactes import GrammarError

try:
    Grammar.from_text("expr NUMBER\nexpr -> NUMBER $\n")
except GrammarError as e:
    print(e.problems)
    # [(1, "expected 'lhs -> symbols'"), (2, "'$' is reserved for the end of the input")]
```

A line is an error if it has no `->`, an invalid name, a `$`, an `ε` next to
other symbols, an unknown primitive, a `%` without a primitive before it, a
value type on a rule without exactly one symbol, [operand positions](#operands)
that aren't valid, or repeats an earlier rule.
The message for an unknown primitive lists the valid names:

```python
try:
    Grammar.from_text("integer % expr -> NUMBER\n")
except GrammarError as e:
    print(e.problems)
    # [(1, 'invalid primitive integer expected one of int, float, str, None, bool, add, sub, mul, div, pow, lt, le, gt, ge, eq, ne')]

try:
    Grammar.from_text("add(1,4) % expr -> expr PLUS expr\nint(1) % expr -> NUMBER\n")
except GrammarError as e:
    print(e.problems)
    # [(1, 'operand position 4 is out of range 1-3'), (2, 'int takes no operand positions')]
```

### Warnings

A valid grammar that is probably not what was intended emits a
`GrammarWarning` through the `warnings` module. There's one for each
non-terminal that can't be reached from the start symbol, and one for each
non-terminal that can't derive a string of terminals. Each warning carries its
`line` and `message`.

```python
import warnings
from syntactes import GrammarWarning

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always", GrammarWarning)
    Grammar.from_text("expr -> NUMBER\nunused -> NAME\nloop -> loop NAME\n")

for warning in caught:
    print(warning.message.line, warning.message.message)
```

```
2 non-terminal 'unused' can't be reached from the start symbol 'expr'
3 non-terminal 'loop' can't be reached from the start symbol 'expr'
3 non-terminal 'loop' can't derive a string of terminals
```

## Building a grammar from objects

A `Token` is a symbol, and is either a terminal or a non-terminal. `Token.eof()`
is the end of the input (`$`), and `Token.null()` is the empty string (`ε`).

A `Rule` takes a number, its left-hand side and its right-hand side symbols.
A `Grammar` takes the starting rule, every rule (the starting rule included)
and the set of tokens.

```python
from syntactes import Grammar, Rule, Token

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
```

An empty rule can be written as `Rule(n, A)` or
`Rule(n, A, Token.null())`.

To give rules primitives, pass `Grammar` a mapping from rules to
`syntactes.primitive` classes as the keyword argument `primitives`, as in
`Grammar(rule_1, rules, tokens, primitives={rule_4: Integer})`. A rule is
matched by its symbols, not its number. The mapping is copied, and
`grammar.primitives` is read-only.

Operand positions go in the keyword argument `operands`, a mapping from rules
to `(left, right)` pairs, as in `operands={rule_2: (1, 3)}`. A binary
operation without an entry gets its first and last symbols.

Tokens are compared by their symbol and whether they're terminal. A token can
also carry a `value`, which equality and hashing ignore, so `Token("x", True, 1)`
and `Token("x", True)` are the same symbol. The [parser](parsing.md) uses that
value to pass data to your callbacks.

### Errors

`Grammar` raises a `GrammarError` (a `ValueError`) if:

- the starting rule is not in the rules, or doesn't end with `$`;
- `$` appears anywhere other than at the end of the starting rule;
- a rule's left-hand side is a terminal;
- a rule uses a symbol that is not in the tokens (`ε` is always allowed);
- a non-terminal has no rules;
- two rules have the same number;
- a primitive is given for a rule that's not in the rules, or isn't one of
  `syntactes.primitive.primitives()`;
- operands are given for a rule that's not in the rules, or whose primitive
  isn't a binary operation;
- a binary operation's rule has fewer than 2 symbols, or its operand positions
  are equal or out of range;
- a value type other than `None` tags a rule without exactly one symbol.

It stops at the first problem, and `problems` holds its message as
`[(None, message)]`.
