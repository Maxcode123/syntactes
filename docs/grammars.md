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
other symbols, or repeats an earlier rule.

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

An empty rule can be written as `Rule(n, A)` or `Rule(n, A, Token.null())`.

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
- two rules have the same number.

It stops at the first problem, and `problems` holds its message as
`[(None, message)]`.
