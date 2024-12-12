from unittest_extensions import TestCase, args

from syntactes._action import Action, ActionType
from syntactes._item import LR0Item
from syntactes.generator import LR0Generator, SLRGenerator
from syntactes.tests.data import (
    EOF,
    PLUS,
    E,
    T,
    grammar_1,
    rule_2_1,
    rule_3_1,
    rule_4_1,
    lr0_state_1,
    lr0_state_2,
    lr0_state_3,
    lr0_state_4,
    lr0_state_5,
    lr0_state_6,
    x,
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
