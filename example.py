from syntactes.generator import LR0Generator
from syntactes.grammar import Grammar
from syntactes.rule import Rule
from syntactes.token import Token

EOF = Token.eof()
S = Token("S", False)
E = Token("E", False)
T = Token("T", False)
x = Token("x", True)
PLUS = Token("+", True)

tokens = {EOF, S, E, T, x, PLUS}


# S -> E $
rule_1 = Rule(0, S, E, EOF)
# E -> T + E
rule_2 = Rule(1, E, T, PLUS, E)
# E -> T
rule_3 = Rule(2, E, T)
# T -> x
rule_4 = Rule(3, T, x)

rules = (rule_1, rule_2, rule_3, rule_4)

grammar = Grammar(rule_1, rules, tokens)

generator = LR0Generator(grammar)

table = generator.generate()

print(table.pretty_str())

