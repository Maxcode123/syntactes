from syntactes import Grammar, Rule, Token
from syntactes._item import LR0Item
from syntactes._state import LR0State

EOF = Token.eof()
S = Token("S", False)
E = Token("E", False)
T = Token("T", False)
x = Token("x", True)
PLUS = Token("+", True)

tokens = {EOF, S, E, T, x, PLUS}


# 1. S -> E $
# 2. E -> T + E
# 3. E -> T
# 4. T -> x
rule_1 = Rule(0, S, E, EOF)
rule_2 = Rule(1, E, T, PLUS, E)
rule_3 = Rule(2, E, T)
rule_4 = Rule(3, T, x)

rules = (rule_1, rule_2, rule_3, rule_4)

grammar = Grammar(rule_1, rules, tokens)


def state_1():
    item_1 = LR0Item(grammar.starting_rule, 0)  # S -> . E $
    item_2 = LR0Item(rule_2, 0)  # E -> . T + E
    item_3 = LR0Item(rule_3, 0)  # E -> . T
    item_4 = LR0Item(rule_4, 0)  # T -> . x
    state = LR0State.from_items({item_1, item_2, item_3, item_4})
    state.set_number(1)
    return state


def state_2():
    item_1 = LR0Item(grammar.starting_rule, 1)  # S -> E . $
    state = LR0State.from_items({item_1})
    state.set_number(2)
    return state


def state_3():
    item_1 = LR0Item(rule_2, 1)  # E -> T . + E
    item_2 = LR0Item(rule_3, 1)  # E -> T .
    state = LR0State.from_items({item_1, item_2})
    state.set_number(3)
    return state


def state_4():
    item_1 = LR0Item(rule_2, 2)  # E -> T + . E
    item_2 = LR0Item(rule_2, 0)  # E -> . T + E
    item_3 = LR0Item(rule_3, 0)  # E -> . T
    item_4 = LR0Item(rule_4, 0)  # T -> . x
    state = LR0State.from_items({item_1, item_2, item_3, item_4})
    state.set_number(4)
    return state


def state_5():
    item_1 = LR0Item(rule_4, 1)  # T -> x .
    state = LR0State.from_items({item_1})
    state.set_number(5)
    return state


def state_6():
    item_1 = LR0Item(rule_2, 3)  # E -> T + E .
    state = LR0State.from_items({item_1})
    state.set_number(6)
    return state
