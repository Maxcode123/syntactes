from syntactes import Grammar, Rule, Symbol, Token
from syntactes.parser import ParserError, SLRParser

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
    return Token(x, value)


plus, eof = Token(PLUS), Token(EOF)

print("Parsing stream: 1 + 2 + 3 $\n")
print("result:", parser.parse([num(1), plus, num(2), plus, num(3), eof]))

print("\nParsing stream: 1 + $\n")
try:
    parser.parse([num(1), plus, eof])
except ParserError as e:
    print("ParserError:", e)
