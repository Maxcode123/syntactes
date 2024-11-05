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
