from syntactes import Grammar, Rule, Token
from syntactes._action import Action
from syntactes._item import LR0Item, LR1Item
from syntactes._state import LR0State, LR1State
from syntactes.parsing_table import (
    Entry,
    LR0ParsingTable,
    LR1ParsingTable,
    SLRParsingTable,
)

EOF = Token.eof()
S = Token("S", False)
E = Token("E", False)
T = Token("T", False)
L = Token("L", False)
C = Token("C", False)
x = Token("x", True)
PLUS = Token("+", True)
LPAREN = Token("(", True)
RPAREN = Token(")", True)

tokens_1 = {EOF, S, E, T, x, PLUS}
tokens_2 = {EOF, S, L, C, LPAREN, RPAREN}

# 1. S -> E $
# 2. E -> T + E
# 3. E -> T
# 4. T -> x
rule_1_1 = Rule(0, None, S, E, EOF)
rule_2_1 = Rule(1, None, E, T, PLUS, E)
rule_3_1 = Rule(2, None, E, T)
rule_4_1 = Rule(3, None, T, x)

rules_1 = (rule_1_1, rule_2_1, rule_3_1, rule_4_1)

grammar_1 = Grammar(rule_1_1, rules_1, tokens_1)

# 1. S -> L $
# 2. L -> L C
# 3. L -> C
# 4. C -> LPAREN C RPAREN
# 5. C -> LPAREN RPAREN
rule_1_2 = Rule(0, None, S, L, EOF)
rule_2_2 = Rule(1, None, L, L, C)
rule_3_2 = Rule(2, None, L, C)
rule_4_2 = Rule(3, None, C, LPAREN, C, RPAREN)
rule_5_2 = Rule(4, None, C, LPAREN, RPAREN)

rules_2 = (rule_1_2, rule_2_2, rule_3_2, rule_4_2, rule_5_2)

grammar_2 = Grammar(rule_1_2, rules_2, tokens_2)

A = Token("A", False)
B = Token("B", False)
a = Token("a", True)
y = Token("y", True)
NULL = Token.null()

tokens_3 = {EOF, S, E, T, x, PLUS}
tokens_4 = {EOF, S, A, E, a, x, NULL}
tokens_5 = {EOF, S, A, B, x, y}
tokens_6 = {EOF, S, E, x, PLUS}

# Closure without a chain of unit rules.
# 0. S -> E $
# 1. E -> T + x
# 2. T -> x
rule_1_3 = Rule(0, None, S, E, EOF)
rule_2_3 = Rule(1, None, E, T, PLUS, x)
rule_3_3 = Rule(2, None, T, x)

rules_3 = (rule_1_3, rule_2_3, rule_3_3)

grammar_3 = Grammar(rule_1_3, rules_3, tokens_3)

# Nullable symbol.
# 0. S -> A E $
# 1. A -> a
# 2. A -> ε
# 3. E -> x
rule_1_4 = Rule(0, None, S, A, E, EOF)
rule_2_4 = Rule(1, None, A, a)
rule_3_4 = Rule(2, None, A, NULL)
rule_4_4 = Rule(3, None, E, x)

rules_4 = (rule_1_4, rule_2_4, rule_3_4, rule_4_4)

grammar_4 = Grammar(rule_1_4, rules_4, tokens_4)

# Mutual tail recursion.
# 0. S -> A $
# 1. A -> x B
# 2. B -> y A
# 3. B -> y
rule_1_5 = Rule(0, None, S, A, EOF)
rule_2_5 = Rule(1, None, A, x, B)
rule_3_5 = Rule(2, None, B, y, A)
rule_4_5 = Rule(3, None, B, y)

rules_5 = (rule_1_5, rule_2_5, rule_3_5, rule_4_5)

grammar_5 = Grammar(rule_1_5, rules_5, tokens_5)

# Ambiguous, with a shift/reduce conflict.
# 0. S -> E $
# 1. E -> E + E
# 2. E -> x
rule_1_6 = Rule(0, None, S, E, EOF)
rule_2_6 = Rule(1, None, E, E, PLUS, E)
rule_3_6 = Rule(2, None, E, x)

rules_6 = (rule_1_6, rule_2_6, rule_3_6)

grammar_6 = Grammar(rule_1_6, rules_6, tokens_6)

tokens_7 = {EOF, S, T, A, a, x, y, NULL}

# Nullable symbol followed by more symbols.
# 0. S -> T A x $
# 1. T -> y
# 2. A -> a
# 3. A -> ε
rule_1_7 = Rule(0, None, S, T, A, x, EOF)
rule_2_7 = Rule(1, None, T, y)
rule_3_7 = Rule(2, None, A, a)
rule_4_7 = Rule(3, None, A, NULL)

rules_7 = (rule_1_7, rule_2_7, rule_3_7, rule_4_7)

grammar_7 = Grammar(rule_1_7, rules_7, tokens_7)

# Same as grammar_4, with the empty rule written without ε.
# 0. S -> A E $
# 1. A -> a
# 2. A ->
# 3. E -> x
rule_3_8 = Rule(2, None, A)

rules_8 = (rule_1_4, rule_2_4, rule_3_8, rule_4_4)

grammar_8 = Grammar(rule_1_4, rules_8, tokens_4)


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


def lr1_state_1():
    item_1 = LR1Item(rule_1_2, 0, EOF)  # S -> . L $, $
    item_2 = LR1Item(rule_2_2, 0, EOF)  # L -> . L C, $
    item_3 = LR1Item(rule_2_2, 0, LPAREN)  # L -> . L C, (
    item_4 = LR1Item(rule_3_2, 0, EOF)  # L -> . C, $
    item_5 = LR1Item(rule_3_2, 0, LPAREN)  # L -> . C, (
    item_6 = LR1Item(rule_4_2, 0, EOF)  # C -> . ( C ), $
    item_7 = LR1Item(rule_4_2, 0, LPAREN)  # C -> . ( C ), (
    item_8 = LR1Item(rule_5_2, 0, EOF)  # C -> . (), $
    item_9 = LR1Item(rule_5_2, 0, LPAREN)  # C -> . (), (
    state = LR1State.from_items(
        {item_1, item_2, item_3, item_4, item_5, item_6, item_7, item_8, item_9}
    )
    state.set_number(1)
    return state


def lr1_state_2():
    item_1 = LR1Item(rule_1_2, 1, EOF)  # S -> L . $, $
    item_2 = LR1Item(rule_2_2, 1, EOF)  # L -> L . C, $
    item_3 = LR1Item(rule_2_2, 1, LPAREN)  # L -> L . C, (
    item_4 = LR1Item(rule_4_2, 0, EOF)  # C -> . ( C ), $
    item_5 = LR1Item(rule_4_2, 0, LPAREN)  # C -> . ( C ), (
    item_6 = LR1Item(rule_5_2, 0, EOF)  # C -> . ( ), $
    item_7 = LR1Item(rule_5_2, 0, LPAREN)  # C -> . ( ), (
    state = LR1State.from_items(
        {item_1, item_2, item_3, item_4, item_5, item_6, item_7}
    )
    state.set_number(2)
    state.set_final()
    return state


def lr1_state_3():
    item_1 = LR1Item(rule_3_2, 1, EOF)  # L -> C ., $
    item_2 = LR1Item(rule_3_2, 1, LPAREN)  # L -> C ., (
    state = LR1State.from_items({item_1, item_2})
    state.set_number(3)
    return state


def lr1_state_4():
    item_1 = LR1Item(rule_4_2, 0, RPAREN)  # C -> . ( C ), )
    item_2 = LR1Item(rule_4_2, 1, EOF)  # C -> ( . C ), $
    item_3 = LR1Item(rule_4_2, 1, LPAREN)  # C -> ( . C ), (
    item_4 = LR1Item(rule_5_2, 0, RPAREN)  # C -> . ( ), )
    item_5 = LR1Item(rule_5_2, 1, EOF)  # C -> ( . ), $
    item_6 = LR1Item(rule_5_2, 1, LPAREN)  # C -> ( . ), (
    state = LR1State.from_items({item_1, item_2, item_3, item_4, item_5, item_6})
    state.set_number(4)
    return state


def lr1_state_5():
    item_1 = LR1Item(rule_2_2, 2, EOF)  # L -> L C ., $
    item_2 = LR1Item(rule_2_2, 2, LPAREN)  # L -> L C ., (
    state = LR1State.from_items({item_1, item_2})
    state.set_number(5)
    return state


def lr1_state_6():
    item_1 = LR1Item(rule_4_2, 2, EOF)  # C -> ( C . ), $
    item_2 = LR1Item(rule_4_2, 2, LPAREN)  # C -> ( C . ), (
    state = LR1State.from_items({item_1, item_2})
    state.set_number(6)
    return state


def lr1_state_7():
    item_1 = LR1Item(rule_4_2, 0, RPAREN)  # C -> . ( C ), )
    item_2 = LR1Item(rule_4_2, 1, RPAREN)  # C -> ( . C ), )
    item_3 = LR1Item(rule_5_2, 0, RPAREN)  # C -> . ( ), )
    item_4 = LR1Item(rule_5_2, 1, RPAREN)  # C -> ( . ), )
    state = LR1State.from_items({item_1, item_2, item_3, item_4})
    state.set_number(7)
    return state


def lr1_state_8():
    item_1 = LR1Item(rule_5_2, 2, EOF)  # C -> ( ) ., $
    item_2 = LR1Item(rule_5_2, 2, LPAREN)  # C -> ( ) ., (
    state = LR1State.from_items({item_1, item_2})
    state.set_number(8)
    return state


def lr1_state_9():
    item_1 = LR1Item(rule_4_2, 3, EOF)  # C -> ( C ) ., $
    item_2 = LR1Item(rule_4_2, 3, LPAREN)  # C -> ( C ) ., (
    state = LR1State.from_items({item_1, item_2})
    state.set_number(9)
    return state


def lr1_state_10():
    item_1 = LR1Item(rule_4_2, 2, RPAREN)  # C -> ( C . ), )
    state = LR1State.from_items({item_1})
    state.set_number(10)
    return state


def lr1_state_11():
    item_1 = LR1Item(rule_5_2, 2, RPAREN)  # C -> ( ) ., )
    state = LR1State.from_items({item_1})
    state.set_number(11)
    return state


def lr1_state_12():
    item_1 = LR1Item(rule_4_2, 3, RPAREN)  # C -> ( C ) ., )
    state = LR1State.from_items({item_1})
    state.set_number(12)
    return state


def lr1_parsing_table():
    table = LR1ParsingTable(grammar_2)
    table.add_entry(Entry(lr1_state_1(), L, Action.shift(lr1_state_2())))
    table.add_entry(Entry(lr1_state_1(), C, Action.shift(lr1_state_3())))
    table.add_entry(Entry(lr1_state_1(), LPAREN, Action.shift(lr1_state_4())))
    table.add_entry(Entry(lr1_state_2(), C, Action.shift(lr1_state_5())))
    table.add_entry(Entry(lr1_state_2(), LPAREN, Action.shift(lr1_state_4())))
    table.add_entry(Entry(lr1_state_2(), EOF, Action.accept()))
    table.add_entry(Entry(lr1_state_3(), LPAREN, Action.reduce(rule_3_2)))
    table.add_entry(Entry(lr1_state_3(), EOF, Action.reduce(rule_3_2)))
    table.add_entry(Entry(lr1_state_4(), C, Action.shift(lr1_state_6())))
    table.add_entry(Entry(lr1_state_4(), LPAREN, Action.shift(lr1_state_7())))
    table.add_entry(Entry(lr1_state_4(), RPAREN, Action.shift(lr1_state_8())))
    table.add_entry(Entry(lr1_state_5(), LPAREN, Action.reduce(rule_2_2)))
    table.add_entry(Entry(lr1_state_5(), EOF, Action.reduce(rule_2_2)))
    table.add_entry(Entry(lr1_state_6(), RPAREN, Action.shift(lr1_state_9())))
    table.add_entry(Entry(lr1_state_7(), LPAREN, Action.shift(lr1_state_7())))
    table.add_entry(Entry(lr1_state_7(), RPAREN, Action.shift(lr1_state_11())))
    table.add_entry(Entry(lr1_state_7(), C, Action.shift(lr1_state_10())))
    table.add_entry(Entry(lr1_state_8(), LPAREN, Action.reduce(rule_5_2)))
    table.add_entry(Entry(lr1_state_8(), EOF, Action.reduce(rule_5_2)))
    table.add_entry(Entry(lr1_state_9(), LPAREN, Action.reduce(rule_4_2)))
    table.add_entry(Entry(lr1_state_9(), EOF, Action.reduce(rule_4_2)))
    table.add_entry(Entry(lr1_state_10(), RPAREN, Action.shift(lr1_state_12())))
    table.add_entry(Entry(lr1_state_11(), RPAREN, Action.reduce(rule_5_2)))
    table.add_entry(Entry(lr1_state_12(), RPAREN, Action.reduce(rule_4_2)))
    return table
