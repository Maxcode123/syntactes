---
title: What is syntactes?
---

<div class="sx-title" markdown="0">
  <p class="sx-kicker">Parser generator · Python 3.13+</p>
  <p class="sx-logo" aria-hidden="true">SYNTACTES</p>
  <h1 id="what-is-syntactes">Write the grammar.<br>Get the <span>parser.</span></h1>
  <p class="sx-blurb">A small Python parser generator with no dependencies.
  Give it a grammar, and it builds LR0, SLR or LR1 parsing tables, and parsers
  that run your callbacks on every reduction.</p>
  <div class="sx-buttons">
    <a class="md-button md-button--primary" href="installation/">Press start</a>
    <a class="md-button" href="https://github.com/Maxcode123/syntactes">GitHub</a>
  </div>
</div>

`syntactes` is a parser generator written in Python. The name comes from the
Greek _συντάκτης_ (/sin'daktis/), meaning editor or composer.

- **Grammars as text or as objects.** Write one `lhs -> symbols` rule per line,
  or build the `Token`s and `Rule`s yourself. See [Grammars](grammars.md).
- **Three kinds of tables.** LR0, SLR and LR1 generators, with a readable
  printout and a list of conflicts. See [Parsing tables](parsing-tables.md).
- **Callbacks on every reduction.** Each rule's callback gets one token per
  right-hand side symbol, and its return value becomes the value of the
  left-hand side. See [Parsing](parsing.md).
- **No dependencies.** It uses only the standard library.

Here's a calculator in a few lines:

```python
from syntactes import Grammar, Token
from syntactes.parser import LR1Parser

grammar = Grammar.from_text("""
expr -> expr PLUS term
expr -> term
term -> term TIMES NUMBER
term -> NUMBER
""")
start, add, pass_term, multiply, number = grammar.rules

parser = LR1Parser.from_grammar(grammar)


@parser.execute_on(start)
def result(expr):
    return expr.value


@parser.execute_on(add)
def on_add(expr, plus, term):
    return expr.value + term.value


@parser.execute_on(pass_term)
def on_term(term):
    return term.value


@parser.execute_on(multiply)
def on_multiply(term, times, number):
    return term.value * number.value


@parser.execute_on(number)
def on_number(number):
    return number.value


def lex(text):
    for word in text.split():
        if word == "+":
            yield Token("PLUS", True)
        elif word == "*":
            yield Token("TIMES", True)
        else:
            yield Token("NUMBER", True, int(word))
    yield Token.eof()


print(parser.parse(lex("2 * 3 + 4")))  # 10
```

Need a scanner to produce the tokens? The sibling project
[lectes](https://maximosnikiforakis.gr/lectes/) scans text with named regexes,
and its tokens map onto syntactes `Token`s.
