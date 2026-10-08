from string import ascii_lowercase, ascii_uppercase

from syntactes import Grammar, Rule, LR1Generator, Token
from syntactes.parser import LR1Parser

tokens = []
ns = locals()


def token(symbol, is_terminal=True):
    ns[symbol] = Token(symbol, is_terminal)
    tokens.append(ns[symbol])


token("START", False)
token("RE", False)
token("RE2", False)
EOF = Token.eof()
tokens.append(EOF)
NULL = Token.null()
tokens.append(NULL)
CONCAT = Token("·", True)
tokens.append(CONCAT)
VBAR = Token("|", True)
tokens.append(VBAR)
STAR = Token("*", True)
tokens.append(STAR)
PLUS = Token("+", True)
tokens.append(PLUS)
QMARK = Token("?", True)
tokens.append(QMARK)

for char in ascii_lowercase + ascii_uppercase:
    token(char)


zero = Token("0", True)
tokens.append(zero)
one = Token("1", True)
tokens.append(one)
two = Token("2", True)
tokens.append(two)
three = Token("3", True)
tokens.append(three)
four = Token("4", True)
tokens.append(four)
five = Token("5", True)
tokens.append(five)
six = Token("6", True)
tokens.append(six)
seven = Token("7", True)
tokens.append(seven)
eight = Token("8", True)
tokens.append(eight)
nine = Token("9", True)
tokens.append(nine)

rules = []


def rule(*rhs):
    rule = Rule(len(rules) + 1, RE, *rhs)
    rules.append(rule)
    return rule


rules.append(Rule(1, START, RE, EOF))
# rule(RE, CONCAT, RE)
rule(RE, VBAR, RE)
rule(RE, STAR)
rule(RE, PLUS)
rule(RE, QMARK)


# for char in ascii_lowercase + ascii_uppercase:
for char in ["a", "b"]:
    rule(ns[char])
# for i in {zero, one, two, three, four, five, six, seven, eight, nine}:
for i in {zero, one}:
    rule(i)
# 1. START -> RE $
# 2. RE -> RE · RE
# 3. RE -> RE|RE
# 4. RE -> RE*
# 5. RE -> RE+
# 6. RE -> RE?
# 7. RE -> a
# 8. RE -> b
# 9. RE -> c
# 10. RE -> d
# 11. RE -> e
# 12. RE -> f
# 13. RE -> g
# 14. RE -> h
# 15. RE -> i
# 16. RE -> j
# 17. RE -> k
# 18. RE -> l
# 19. RE -> m
# 20. RE -> n
# 21. RE -> o
# 22. RE -> p
# 23. RE -> q
# 24. RE -> r
# 25. RE -> s
# 26. RE -> t
# 27. RE -> u
# 28. RE -> v
# 29. RE -> w
# 30. RE -> x
# 31. RE -> y
# 32. RE -> z
# 33. RE -> A
# 34. RE -> B
# 35. RE -> C
# 36. RE -> D
# 37. RE -> E
# 38. RE -> F
# 39. RE -> G
# 40. RE -> H
# 41. RE -> I
# 42. RE -> J
# 43. RE -> K
# 44. RE -> L
# 45. RE -> M
# 46. RE -> N
# 47. RE -> O
# 48. RE -> P
# 49. RE -> Q
# 50. RE -> R
# 51. RE -> S
# 52. RE -> T
# 53. RE -> U
# 54. RE -> V
# 55. RE -> W
# 56. RE -> X
# 57. RE -> Y
# 58. RE -> Z
# 59. RE -> 0
# 60. RE -> 1
# 61. RE -> 2
# 62. RE -> 3
# 63. RE -> 4
# 64. RE -> 5
# 65. RE -> 6
# 66. RE -> 7
# 67. RE -> 8
# 68. RE -> 9

grammar = Grammar(rules[0], rules, tokens)

generator = LR1Generator(grammar)

table = generator.generate()

parser = LR1Parser(table)

for c in table.conflicts():
    print(c.pretty_str())

print(len(table.conflicts()), "conflicts")
