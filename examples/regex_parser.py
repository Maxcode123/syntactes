from string import ascii_lowercase, ascii_uppercase

from syntactes import Grammar, LR1Generator, Rule, Symbol
from syntactes.parser import LR1Parser

symbols = []
ns = locals()


def symbol(name, is_terminal=True):
    ns[name] = Symbol(name, is_terminal)
    symbols.append(ns[name])


symbol("START", False)
symbol("RE", False)
symbol("RE2", False)
EOF = Symbol.eof()
symbols.append(EOF)
NULL = Symbol.null()
symbols.append(NULL)
CONCAT = Symbol("·", True)
symbols.append(CONCAT)
VBAR = Symbol("|", True)
symbols.append(VBAR)
STAR = Symbol("*", True)
symbols.append(STAR)
PLUS = Symbol("+", True)
symbols.append(PLUS)
QMARK = Symbol("?", True)
symbols.append(QMARK)

for char in ascii_lowercase + ascii_uppercase:
    symbol(char)


zero = Symbol("0", True)
symbols.append(zero)
one = Symbol("1", True)
symbols.append(one)
two = Symbol("2", True)
symbols.append(two)
three = Symbol("3", True)
symbols.append(three)
four = Symbol("4", True)
symbols.append(four)
five = Symbol("5", True)
symbols.append(five)
six = Symbol("6", True)
symbols.append(six)
seven = Symbol("7", True)
symbols.append(seven)
eight = Symbol("8", True)
symbols.append(eight)
nine = Symbol("9", True)
symbols.append(nine)

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

grammar = Grammar(rules[0], rules, symbols)

generator = LR1Generator(grammar)

table = generator.generate()

parser = LR1Parser(table)

for c in table.conflicts():
    print(c.pretty_str())

print(len(table.conflicts()), "conflicts")
