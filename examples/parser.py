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
