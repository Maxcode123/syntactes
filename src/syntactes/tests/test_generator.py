from unittest_extensions import TestCase, args

from syntactes._action import Action, ActionType
from syntactes._item import LR0Item, LR1Item
from syntactes.generator import LR0Generator, LR1Generator, SLRGenerator
from syntactes.tests.data import (
    EOF,
    LPAREN,
    NULL,
    PLUS,
    RPAREN,
    A,
    B,
    C,
    E,
    L,
    S,
    T,
    a,
    grammar_1,
    grammar_2,
    grammar_3,
    grammar_4,
    grammar_5,
    grammar_7,
    grammar_8,
    lr0_state_1,
    lr0_state_2,
    lr0_state_3,
    lr0_state_4,
    lr0_state_5,
    lr0_state_6,
    lr1_state_1,
    lr1_state_2,
    lr1_state_3,
    lr1_state_4,
    lr1_state_5,
    lr1_state_6,
    lr1_state_7,
    lr1_state_8,
    lr1_state_9,
    lr1_state_10,
    lr1_state_11,
    lr1_state_12,
    rule_2_1,
    rule_2_2,
    rule_3_1,
    rule_3_2,
    rule_4_1,
    rule_4_2,
    rule_5_2,
    x,
    y,
)


def shift(state):
    return Action(state, ActionType.SHIFT)


def reduce(rule):
    return Action(rule, ActionType.REDUCE)


def accept():
    return Action(None, ActionType.ACCEPT)


class TestLR0Generator(TestCase):
    def setUp(self):
        self._generator = LR0Generator(grammar_1)

    def generator(self):
        return self._generator

    def assert_items(self, items):
        self.assertSetEqual(set(map(str, self.result())), items)


class TestLR0GeneratorClosure(TestLR0Generator):
    def subject(self, items):
        return self.generator().closure(items)

    # S -> . E $
    @args({LR0Item(grammar_1.starting_rule, 0)})
    def test_with_starting_item(self):
        self.assert_items({"S -> . E $", "E -> . T + E", "E -> . T", "T -> . x"})

    # E -> . T
    @args({LR0Item(rule_3_1, 0)})
    def test_with_rule3_first_item(self):
        self.assert_items({"E -> . T", "T -> . x"})

    # T -> . x
    @args({LR0Item(rule_4_1, 0)})
    def test_with_rule4_first_item(self):
        self.assert_items({"T -> . x"})

    # E -> T + . E
    @args({LR0Item(rule_2_1, 2)})
    def test_with_rule2_third_item(self):
        self.assert_items({"E -> T + . E", "E -> . T + E", "E -> . T", "T -> . x"})


class TestLR0GeneratorGoto(TestLR0Generator):
    def subject(self, items, token):
        return self.generator().goto(items, token)

    # S -> . E $
    @args({LR0Item(grammar_1.starting_rule, 0)}, T)
    def test_starting_item_with_other_token(self):
        self.assert_items(set())

    # S -> . E $
    @args({LR0Item(grammar_1.starting_rule, 0)}, E)
    def test_starting_item(self):
        self.assert_items({"S -> E . $"})

    # E -> T + . E
    @args({LR0Item(rule_2_1, 2)}, E)
    def test_with_rule2_third_item(self):
        self.assert_items({"E -> T + E ."})

    # E -> T . + E
    @args({LR0Item(rule_2_1, 1)}, PLUS)
    def test_with_rule2_second_item(self):
        self.assert_items({"E -> T + . E", "E -> . T + E", "E -> . T", "T -> . x"})


class TestLR0GeneratorGetStates(TestLR0Generator):
    def subject(self):
        return self.generator().get_states()

    def test_get_states(self):
        self.assertResultSet(
            {
                lr0_state_1(),
                lr0_state_2(),
                lr0_state_3(),
                lr0_state_4(),
                lr0_state_5(),
                lr0_state_6(),
            }
        )


class TestLR0GeneratorGenerateEntries(TestLR0Generator):
    def subject(self, state):
        return self.generator().generate().get(state)

    def assert_state_entries(self, *state_entries):
        self.assertCountEqual(self.result().keys(), state_entries)

    # S -> . E $
    # E -> . T + E
    # E -> . T
    # T -> . x
    @args(lr0_state_1())
    def test_lr0_state_1_entries(self):
        self.assert_state_entries(x, E, T)

    # S -> E . $
    @args(lr0_state_2())
    def test_lr0_state_2_entries(self):
        self.assert_state_entries(EOF)

    # E -> T . + E
    # E -> T .
    @args(lr0_state_3())
    def test_lr0_state_3_entries(self):
        self.assert_state_entries(x, PLUS, EOF)

    # E -> T + . E
    # E -> . T + E
    # E -> . T
    # T -> . x
    @args(lr0_state_4())
    def test_lr0_state_4_entries(self):
        self.assert_state_entries(x, E, T)

    @args(lr0_state_5())
    def test_lr0_state_5_entries(self):
        # T -> x .
        self.assert_state_entries(x, PLUS, EOF)

    # E -> T + E .
    @args(lr0_state_6())
    def test_lr0_state_6_entries(self):
        self.assert_state_entries(x, PLUS, EOF)


class TestLR0GeneratorGenerateActions(TestLR0Generator):
    def subject(self, state, token):
        return self.generator().generate().get(state).get(token)

    def assert_state_actions(self, *state_actions):
        self.assertCountEqual(self.result(), state_actions)

    @args(lr0_state_1(), E)
    def test_lr0_state_1_token_E(self):
        self.assert_state_actions(shift(lr0_state_2()))

    @args(lr0_state_1(), T)
    def test_lr0_state_1_token_T(self):
        self.assert_state_actions(shift(lr0_state_3()))

    @args(lr0_state_1(), x)
    def test_lr0_state_1_token_x(self):
        self.assert_state_actions(shift(lr0_state_5()))

    @args(lr0_state_2(), EOF)
    def test_lr0_state_2_token_eof(self):
        self.assert_state_actions(accept())

    @args(lr0_state_3(), PLUS)
    def test_lr0_state_3_token_plus(self):
        self.assert_state_actions(reduce(rule_3_1), shift(lr0_state_4()))

    @args(lr0_state_3(), EOF)
    def test_lr0_state_3_token_eof(self):
        self.assert_state_actions(reduce(rule_3_1))

    @args(lr0_state_3(), x)
    def test_lr0_state_3_token_x(self):
        self.assert_state_actions(reduce(rule_3_1))

    @args(lr0_state_4(), x)
    def test_lr0_state_4_token_x(self):
        self.assert_state_actions(shift(lr0_state_5()))

    @args(lr0_state_4(), E)
    def test_lr0_state_4_token_E(self):
        self.assert_state_actions(shift(lr0_state_6()))

    @args(lr0_state_4(), T)
    def test_lr0_state_4_token_T(self):
        self.assert_state_actions(shift(lr0_state_3()))

    @args(lr0_state_5(), PLUS)
    def test_lr0_state_5_token_plus(self):
        self.assert_state_actions(reduce(rule_4_1))

    @args(lr0_state_5(), EOF)
    def test_lr0_state_5_token_eof(self):
        self.assert_state_actions(reduce(rule_4_1))

    @args(lr0_state_5(), x)
    def test_lr0_state_5_token_x(self):
        self.assert_state_actions(reduce(rule_4_1))

    @args(lr0_state_6(), EOF)
    def test_lr0_state_6_token_eof(self):
        self.assert_state_actions(reduce(rule_2_1))

    @args(lr0_state_6(), PLUS)
    def test_lr0_state_6_token_plus(self):
        self.assert_state_actions(reduce(rule_2_1))

    @args(lr0_state_6(), x)
    def test_lr0_state_6_token_x(self):
        self.assert_state_actions(reduce(rule_2_1))


class TestLR0GeneratorGenerateInitialState(TestLR0Generator):
    def subject(self):
        return self.generator().generate().initial_state

    def test_initial_state(self):
        self.assertResult(lr0_state_1())


class TestSLRGenerator(TestCase):
    def setUp(self):
        self._generator = SLRGenerator(grammar_1)

    def generator(self):
        return self._generator


class TestSLRGeneratorGenerateEntries(TestSLRGenerator):
    def subject(self, state):
        return self.generator().generate().get(state)

    def assert_state_entries(self, *state_entries):
        self.assertCountEqual(self.result().keys(), state_entries)

    # S -> . E $
    # E -> . T + E
    # E -> . T
    # T -> . x
    @args(lr0_state_1())
    def test_lr0_state_1_entries(self):
        self.assert_state_entries(x, E, T)

    # S -> E . $
    @args(lr0_state_2())
    def test_lr0_state_2_entries(self):
        self.assert_state_entries(EOF)

    # E -> T . + E
    # E -> T .
    @args(lr0_state_3())
    def test_lr0_state_3_entries(self):
        self.assert_state_entries(PLUS, EOF)

    # E -> T + . E
    # E -> . T + E
    # E -> . T
    # T -> . x
    @args(lr0_state_4())
    def test_lr0_state_4_entries(self):
        self.assert_state_entries(x, E, T)

    @args(lr0_state_5())
    def test_lr0_state_5_entries(self):
        # T -> x .
        self.assert_state_entries(PLUS, EOF)

    # E -> T + E .
    @args(lr0_state_6())
    def test_lr0_state_6_entries(self):
        self.assert_state_entries(EOF)


class TestSLRGeneratorGenerateActions(TestSLRGenerator):
    def subject(self, state, token):
        return self.generator().generate().get(state).get(token)

    def assert_state_actions(self, *state_actions):
        self.assertCountEqual(self.result(), state_actions)

    @args(lr0_state_1(), E)
    def test_lr0_state_1_token_E(self):
        self.assert_state_actions(shift(lr0_state_2()))

    @args(lr0_state_1(), T)
    def test_lr0_state_1_token_T(self):
        self.assert_state_actions(shift(lr0_state_3()))

    @args(lr0_state_1(), x)
    def test_lr0_state_1_token_x(self):
        self.assert_state_actions(shift(lr0_state_5()))

    @args(lr0_state_2(), EOF)
    def test_lr0_state_2_token_eof(self):
        self.assert_state_actions(accept())

    @args(lr0_state_3(), PLUS)
    def test_lr0_state_3_token_plus(self):
        self.assert_state_actions(shift(lr0_state_4()))

    @args(lr0_state_3(), EOF)
    def test_lr0_state_3_token_eof(self):
        self.assert_state_actions(reduce(rule_3_1))

    @args(lr0_state_4(), x)
    def test_lr0_state_4_token_x(self):
        self.assert_state_actions(shift(lr0_state_5()))

    @args(lr0_state_4(), E)
    def test_lr0_state_4_token_E(self):
        self.assert_state_actions(shift(lr0_state_6()))

    @args(lr0_state_4(), T)
    def test_lr0_state_4_token_T(self):
        self.assert_state_actions(shift(lr0_state_3()))

    @args(lr0_state_5(), PLUS)
    def test_lr0_state_5_token_plus(self):
        self.assert_state_actions(reduce(rule_4_1))

    @args(lr0_state_5(), EOF)
    def test_lr0_state_5_token_eof(self):
        self.assert_state_actions(reduce(rule_4_1))

    @args(lr0_state_6(), EOF)
    def test_lr0_state_6_token_eof(self):
        self.assert_state_actions(reduce(rule_2_1))


class TestSLRGeneratorGenerateInitialState(TestSLRGenerator):
    def subject(self):
        return self.generator().generate().initial_state

    def test_initial_state(self):
        self.assertResult(lr0_state_1())


class TestLR1Generator(TestCase):
    def setUp(self):
        self._generator = LR1Generator(grammar_2)

    def generator(self):
        return self._generator

    def assert_items(self, items):
        self.assertSetEqual(set(map(str, self.result())), items)


class TestLR1GeneratorGetStates(TestLR1Generator):
    def subject(self):
        return self.generator().get_states()

    def test_get_states(self):
        self.assertResultSet(
            {
                lr1_state_1(),
                lr1_state_2(),
                lr1_state_3(),
                lr1_state_4(),
                lr1_state_5(),
                lr1_state_6(),
                lr1_state_7(),
                lr1_state_8(),
                lr1_state_9(),
                lr1_state_10(),
                lr1_state_11(),
                lr1_state_12(),
            }
        )


class TestLR1GeneratorGenerateEntries(TestLR1Generator):
    def subject(self, state):
        return self.generator().generate().get(state)

    def assert_state_entries(self, *state_entries):
        self.assertCountEqual(self.result().keys(), state_entries)

    @args(lr1_state_1())
    def test_lr1_state_1_entries(self):
        self.assert_state_entries(L, C, LPAREN)

    @args(lr1_state_2())
    def test_lr1_state_2_entries(self):
        self.assert_state_entries(C, LPAREN, EOF)

    @args(lr1_state_3())
    def test_lr1_state_3_entries(self):
        self.assert_state_entries(EOF, LPAREN)

    @args(lr1_state_4())
    def test_lr1_state_4_entries(self):
        self.assert_state_entries(C, LPAREN, RPAREN)

    @args(lr1_state_5())
    def test_lr1_state_5_entries(self):
        self.assert_state_entries(EOF, LPAREN)

    @args(lr1_state_6())
    def test_lr1_state_6_entries(self):
        self.assert_state_entries(RPAREN)

    @args(lr1_state_7())
    def test_lr1_state_7_entries(self):
        self.assert_state_entries(C, LPAREN, RPAREN)

    @args(lr1_state_8())
    def test_lr1_state_8_entries(self):
        self.assert_state_entries(EOF, LPAREN)

    @args(lr1_state_9())
    def test_lr1_state_9_entries(self):
        self.assert_state_entries(EOF, LPAREN)

    @args(lr1_state_10())
    def test_lr1_state_10_entries(self):
        self.assert_state_entries(RPAREN)

    @args(lr1_state_11())
    def test_lr1_state_11_entries(self):
        self.assert_state_entries(RPAREN)

    @args(lr1_state_12())
    def test_lr1_state_12_entries(self):
        self.assert_state_entries(RPAREN)


class TestLR1GeneratorGenerateActions(TestLR1Generator):
    def subject(self, state, token):
        return self.generator().generate().get(state).get(token)

    def assert_state_actions(self, *state_actions):
        self.assertCountEqual(self.result(), state_actions)

    @args(lr1_state_1(), LPAREN)
    def test_lr1_state_1_token_LPAREN(self):
        self.assert_state_actions(shift(lr1_state_4()))

    @args(lr1_state_1(), L)
    def test_lr1_state_1_token_L(self):
        self.assert_state_actions(shift(lr1_state_2()))

    @args(lr1_state_1(), C)
    def test_lr1_state_1_token_C(self):
        self.assert_state_actions(shift(lr1_state_3()))

    @args(lr1_state_2(), C)
    def test_lr1_state_2_token_C(self):
        self.assert_state_actions(shift(lr1_state_5()))

    @args(lr1_state_2(), LPAREN)
    def test_lr1_state_2_token_LPAREN(self):
        self.assert_state_actions(shift(lr1_state_4()))

    @args(lr1_state_3(), LPAREN)
    def test_lr1_state_3_token_LPAREN(self):
        self.assert_state_actions(reduce(rule_3_2))

    @args(lr1_state_3(), EOF)
    def test_lr1_state_3_token_EOF(self):
        self.assert_state_actions(reduce(rule_3_2))

    @args(lr1_state_4(), C)
    def test_lr1_state_4_token_C(self):
        self.assert_state_actions(shift(lr1_state_6()))

    @args(lr1_state_4(), LPAREN)
    def test_lr1_state_4_token_LPAREN(self):
        self.assert_state_actions(shift(lr1_state_7()))

    @args(lr1_state_4(), RPAREN)
    def test_lr1_state_4_token_RPAREN(self):
        self.assert_state_actions(shift(lr1_state_8()))

    @args(lr1_state_5(), EOF)
    def test_lr1_state_5_token_EOF(self):
        self.assert_state_actions(reduce(rule_2_2))

    @args(lr1_state_5(), LPAREN)
    def test_lr1_state_5_token_LPAREN(self):
        self.assert_state_actions(reduce(rule_2_2))

    @args(lr1_state_6(), RPAREN)
    def test_lr1_state_6_token_RPAREN(self):
        self.assert_state_actions(shift(lr1_state_9()))

    @args(lr1_state_7(), LPAREN)
    def test_lr1_state_7_token_LPAREN(self):
        self.assert_state_actions(shift(lr1_state_7()))

    @args(lr1_state_7(), RPAREN)
    def test_lr1_state_7_token_RPAREN(self):
        self.assert_state_actions(shift(lr1_state_11()))

    @args(lr1_state_7(), C)
    def test_lr1_state_7_token_C(self):
        self.assert_state_actions(shift(lr1_state_10()))

    @args(lr1_state_8(), EOF)
    def test_lr1_state_8_token_EOF(self):
        self.assert_state_actions(reduce(rule_5_2))

    @args(lr1_state_8(), LPAREN)
    def test_lr1_state_8_token_LPAREN(self):
        self.assert_state_actions(reduce(rule_5_2))

    @args(lr1_state_9(), EOF)
    def test_lr1_state_9_token_EOF(self):
        self.assert_state_actions(reduce(rule_4_2))

    @args(lr1_state_9(), LPAREN)
    def test_lr1_state_9_token_LPAREN(self):
        self.assert_state_actions(reduce(rule_4_2))

    @args(lr1_state_10(), RPAREN)
    def test_lr1_state_10_token_RPAREN(self):
        self.assert_state_actions(shift(lr1_state_12()))

    @args(lr1_state_11(), RPAREN)
    def test_lr1_state_11_token_RPAREN(self):
        self.assert_state_actions(reduce(rule_5_2))

    @args(lr1_state_12(), RPAREN)
    def test_lr1_state_12_token_RPAREN(self):
        self.assert_state_actions(reduce(rule_4_2))


class TestLR1GeneratorClosure(TestLR1Generator):
    def subject(self, items):
        return self.generator().closure(items)

    # S -> . L, $
    @args({LR1Item(grammar_2.starting_rule, 0, EOF)})
    def test_with_starting_item(self):
        self.assert_items(
            {
                "S -> . L $, $",
                "L -> . L C, $",
                "L -> . L C, (",
                "L -> . C, $",
                "L -> . C, (",
                "C -> . ( C ), $",
                "C -> . ( C ), (",
                "C -> . ( ), $",
                "C -> . ( ), (",
            }
        )


class TestLR1GeneratorGoto(TestLR1Generator):
    def subject(self, items, token):
        return self.generator().goto(items, token)

    @args(lr1_state_1().items, LPAREN)
    def test_starting_item_with_other_token(self):
        self.assert_items(
            {
                "C -> ( . C ), $",
                "C -> ( . C ), (",
                "C -> ( . ), $",
                "C -> ( . ), (",
                "C -> . ( C ), )",
                "C -> . ( ), )",
            }
        )


class TestGeneratorFirst(TestCase):
    def subject(self, grammar, *symbols):
        return LR0Generator(grammar)._first(*symbols)

    @args(grammar_1, E)
    def test_unit_rule(self):
        self.assertResult({x})

    @args(grammar_3, E)
    def test_leading_non_terminal(self):
        self.assertResult({x})

    @args(grammar_2, L)
    def test_left_recursion(self):
        self.assertResult({LPAREN})

    @args(grammar_4, A)
    def test_nullable_symbol(self):
        self.assertResult({a})

    @args(grammar_4, A, E)
    def test_nullable_prefix(self):
        self.assertResult({a, x})

    @args(grammar_4, S)
    def test_through_nullable_symbol(self):
        self.assertResult({a, x})

    @args(grammar_4, A, A)
    def test_all_nullable(self):
        self.assertResult({a})

    @args(grammar_5, B)
    def test_mutual_recursion(self):
        self.assertResult({y})

    @args(grammar_1, PLUS, E)
    def test_terminal(self):
        self.assertResult({PLUS})

    @args(grammar_1)
    def test_empty_sequence(self):
        self.assertResult(set())


class TestGeneratorFollow(TestCase):
    def subject(self, grammar, symbol):
        return LR0Generator(grammar)._follow(symbol)

    @args(grammar_1, T)
    def test_unit_rule(self):
        self.assertResult({PLUS, EOF})

    @args(grammar_1, E)
    def test_right_recursion(self):
        self.assertResult({EOF})

    @args(grammar_3, T)
    def test_leading_non_terminal(self):
        self.assertResult({PLUS})

    @args(grammar_2, C)
    def test_nested(self):
        self.assertResult({EOF, LPAREN, RPAREN})

    @args(grammar_4, A)
    def test_nullable_symbol(self):
        self.assertResult({x})

    @args(grammar_5, A)
    def test_mutual_tail_recursion_a(self):
        self.assertResult({EOF})

    @args(grammar_5, B)
    def test_mutual_tail_recursion_b(self):
        self.assertResult({EOF})


class TestGeneratorNullable(TestCase):
    def subject(self, grammar):
        return LR0Generator(grammar)._nullable

    @args(grammar_1)
    def test_no_nullable_symbols(self):
        self.assertResult(set())

    @args(grammar_4)
    def test_nullable_symbol(self):
        self.assertResult({A})


class TestLR0GeneratorClosureWithoutUnitRules(TestCase):
    def subject(self, items):
        return LR0Generator(grammar_3).closure(items)

    # S -> . E $
    @args({LR0Item(grammar_3.starting_rule, 0)})
    def test_with_starting_item(self):
        self.assertSetEqual(
            set(map(str, self.result())),
            {"S -> . E $", "E -> . T + x", "T -> . x"},
        )


class TestLR1GeneratorClosureWithNullableSymbols(TestCase):
    def subject(self, grammar, items):
        return LR1Generator(grammar).closure(items)

    def assert_items(self, items):
        self.assertSetEqual(set(map(str, self.result())), items)

    # S -> . E $, $
    @args(grammar_3, {LR1Item(grammar_3.starting_rule, 0, EOF)})
    def test_without_unit_rules(self):
        self.assert_items({"S -> . E $, $", "E -> . T + x, $", "T -> . x, +"})

    # S -> . A E $, $
    @args(grammar_4, {LR1Item(grammar_4.starting_rule, 0, EOF)})
    def test_nullable_symbol(self):
        self.assert_items({"S -> . A E $, $", "A -> . a, x", "A -> . ε, x"})

    # S -> . T A x $, $
    @args(grammar_7, {LR1Item(grammar_7.starting_rule, 0, EOF)})
    def test_nullable_symbol_followed_by_more_symbols(self):
        self.assert_items({"S -> . T A x $, $", "T -> . y, a", "T -> . y, x"})


class TestGeneratorWithEmptyRules(TestCase):
    def subject(self, generator_cls, grammar):
        return generator_cls(grammar).generate()

    def assert_no_null_actions(self):
        for row in self.result().rows.values():
            self.assertNotIn(NULL, row)

    def assert_no_null_column(self):
        lines = self.result().pretty_str().splitlines()
        header = next(line for line in lines if line.startswith("|     |"))
        self.assertNotIn("ε", header)

    @args(LR0Generator, grammar_4)
    def test_lr0_no_null_actions(self):
        self.assert_no_null_actions()

    @args(SLRGenerator, grammar_4)
    def test_slr_no_null_actions(self):
        self.assert_no_null_actions()

    @args(LR1Generator, grammar_4)
    def test_lr1_no_null_actions(self):
        self.assert_no_null_actions()

    @args(SLRGenerator, grammar_4)
    def test_no_null_column(self):
        self.assert_no_null_column()

    @args(SLRGenerator, grammar_8)
    def test_without_null_token_no_null_column(self):
        self.assert_no_null_column()
