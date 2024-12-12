from syntactes import Grammar, Rule, Token
from syntactes._action import Action
from syntactes._item import LR0Item
from syntactes._state import LR0State
from syntactes.parsing_table import Entry, LR0ParsingTable, SLRParsingTable

EOF = Token.eof()
S = Token("S", False)
E = Token("E", False)
T = Token("T", False)
x = Token("x", True)
PLUS = Token("+", True)

tokens_1 = {EOF, S, E, T, x, PLUS}


# 1. S -> E $
# 2. E -> T + E
# 3. E -> T
# 4. T -> x
rule_1_1 = Rule(0, S, E, EOF)
rule_2_1 = Rule(1, E, T, PLUS, E)
rule_3_1 = Rule(2, E, T)
rule_4_1 = Rule(3, T, x)

rules_1 = (rule_1_1, rule_2_1, rule_3_1, rule_4_1)

grammar_1 = Grammar(rule_1_1, rules_1, tokens_1)


def lr0_state_1():
    item_1 = LR0Item(grammar_1.starting_rule, 0)  # S -> . E $
    item_2 = LR0Item(rule_2_1, 0)  # E -> . T + E
    item_3 = LR0Item(rule_3_1, 0)  # E -> . T
    item_4 = LR0Item(rule_4_1, 0)  # T -> . x
    state = LR0State.from_items({item_1, item_2, item_3, item_4})
    state.set_number(1)
    return state


def lr0_state_2():
    item_1 = LR0Item(grammar_1.starting_rule, 1)  # S -> E . $
    state = LR0State.from_items({item_1})
    state.set_number(2)
    state.set_final()
    return state


def lr0_state_3():
    item_1 = LR0Item(rule_2_1, 1)  # E -> T . + E
    item_2 = LR0Item(rule_3_1, 1)  # E -> T .
    state = LR0State.from_items({item_1, item_2})
    state.set_number(3)
    return state


def lr0_state_4():
    item_1 = LR0Item(rule_2_1, 2)  # E -> T + . E
    item_2 = LR0Item(rule_2_1, 0)  # E -> . T + E
    item_3 = LR0Item(rule_3_1, 0)  # E -> . T
    item_4 = LR0Item(rule_4_1, 0)  # T -> . x
    state = LR0State.from_items({item_1, item_2, item_3, item_4})
    state.set_number(4)
    return state


def lr0_state_5():
    item_1 = LR0Item(rule_4_1, 1)  # T -> x .
    state = LR0State.from_items({item_1})
    state.set_number(5)
    return state


def lr0_state_6():
    item_1 = LR0Item(rule_2_1, 3)  # E -> T + E .
    state = LR0State.from_items({item_1})
    state.set_number(6)
    return state


def lr0_parsing_table():
    table = LR0ParsingTable(grammar_1)
    table.add_entry(Entry(lr0_state_1(), E, Action.shift(lr0_state_2())))
    table.add_entry(Entry(lr0_state_1(), T, Action.shift(lr0_state_3())))
    table.add_entry(Entry(lr0_state_1(), x, Action.shift(lr0_state_5())))
    table.add_entry(Entry(lr0_state_2(), EOF, Action.accept()))
    table.add_entry(Entry(lr0_state_3(), x, Action.reduce(rule_3_1)))
    table.add_entry(Entry(lr0_state_3(), PLUS, Action.shift(lr0_state_4())))
    table.add_entry(Entry(lr0_state_3(), PLUS, Action.reduce(rule_3_1)))
    table.add_entry(Entry(lr0_state_3(), EOF, Action.reduce(rule_3_1)))
    table.add_entry(Entry(lr0_state_4(), x, Action.shift(lr0_state_5())))
    table.add_entry(Entry(lr0_state_4(), E, Action.shift(lr0_state_6())))
    table.add_entry(Entry(lr0_state_4(), T, Action.shift(lr0_state_3())))
    table.add_entry(Entry(lr0_state_5(), x, Action.reduce(rule_4_1)))
    table.add_entry(Entry(lr0_state_5(), PLUS, Action.reduce(rule_4_1)))
    table.add_entry(Entry(lr0_state_5(), EOF, Action.reduce(rule_4_1)))
    table.add_entry(Entry(lr0_state_6(), x, Action.reduce(rule_2_1)))
    table.add_entry(Entry(lr0_state_6(), PLUS, Action.reduce(rule_2_1)))
    table.add_entry(Entry(lr0_state_6(), EOF, Action.reduce(rule_2_1)))
    return table


def slr_parsing_table():
    table = SLRParsingTable(grammar_1)
    table.add_entry(Entry(lr0_state_1(), x, Action.shift(lr0_state_5())))
    table.add_entry(Entry(lr0_state_1(), E, Action.shift(lr0_state_2())))
    table.add_entry(Entry(lr0_state_1(), T, Action.shift(lr0_state_3())))
    table.add_entry(Entry(lr0_state_2(), EOF, Action.accept()))
    table.add_entry(Entry(lr0_state_3(), PLUS, Action.shift(lr0_state_4())))
    table.add_entry(Entry(lr0_state_3(), EOF, Action.reduce(rule_3_1)))
    table.add_entry(Entry(lr0_state_4(), x, Action.shift(lr0_state_5())))
    table.add_entry(Entry(lr0_state_4(), E, Action.shift(lr0_state_6())))
    table.add_entry(Entry(lr0_state_4(), T, Action.shift(lr0_state_3())))
    table.add_entry(Entry(lr0_state_5(), PLUS, Action.reduce(rule_4_1)))
    table.add_entry(Entry(lr0_state_5(), EOF, Action.reduce(rule_4_1)))
    table.add_entry(Entry(lr0_state_6(), EOF, Action.reduce(rule_2_1)))
    return table
