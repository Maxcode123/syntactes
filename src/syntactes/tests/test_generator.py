from unittest_extensions import TestCase, args

from syntactes._action import Action, ActionType
from syntactes._item import LR0Item
from syntactes._state import LR0State
from syntactes.generator import LR0Generator, SLRGenerator
from syntactes.tests.data import EOF, PLUS, E, T, grammar, rule_2, rule_3, rule_4, x


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


def shift(state):
    return Action(state, ActionType.SHIFT)


def reduce(rule):
    return Action(rule, ActionType.REDUCE)


def accept(rule):
    return Action(rule, ActionType.ACCEPT)


class TestLR0Generator(TestCase):
    def setUp(self):
        self._generator = LR0Generator(grammar)

    def generator(self):
        return self._generator

    def assert_items(self, items):
        self.assertSetEqual(set(map(str, self.result())), items)


class TestLR0GeneratorClosure(TestLR0Generator):
    def subject(self, items):
        return self.generator().closure(items)

    # S -> . E $
    @args({LR0Item(grammar.starting_rule, 0)})
    def test_with_starting_item(self):
        self.assert_items({"S -> . E $", "E -> . T + E", "E -> . T", "T -> . x"})

    # E -> . T
    @args({LR0Item(rule_3, 0)})
    def test_with_rule3_first_item(self):
        self.assert_items({"E -> . T", "T -> . x"})

    # T -> . x
    @args({LR0Item(rule_4, 0)})
    def test_with_rule4_first_item(self):
        self.assert_items({"T -> . x"})

    # E -> T + . E
    @args({LR0Item(rule_2, 2)})
    def test_with_rule2_third_item(self):
        self.assert_items({"E -> T + . E", "E -> . T + E", "E -> . T", "T -> . x"})


class TestLR0GeneratorGoto(TestLR0Generator):
    def subject(self, items, token):
        return self.generator().goto(items, token)

    # S -> . E $
    @args({LR0Item(grammar.starting_rule, 0)}, T)
    def test_starting_item_with_other_token(self):
        self.assert_items(set())

    # S -> . E $
    @args({LR0Item(grammar.starting_rule, 0)}, E)
    def test_starting_item(self):
        self.assert_items({"S -> E . $"})

    # E -> T + . E
    @args({LR0Item(rule_2, 2)}, E)
    def test_with_rule2_third_item(self):
        self.assert_items({"E -> T + E ."})

    # E -> T . + E
    @args({LR0Item(rule_2, 1)}, PLUS)
    def test_with_rule2_second_item(self):
        self.assert_items({"E -> T + . E", "E -> . T + E", "E -> . T", "T -> . x"})


class TestLR0GeneratorGetStates(TestLR0Generator):
    def subject(self):
        return self.generator().get_states()

    def test_get_states(self):
        self.assertResultSet(
            {
                state_1(),
                state_2(),
                state_3(),
                state_4(),
                state_5(),
                state_6(),
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
    @args(state_1())
    def test_state_1_entries(self):
        self.assert_state_entries(x, E, T)

    # S -> E . $
    @args(state_2())
    def test_state_2_entries(self):
        self.assert_state_entries(EOF)

    # E -> T . + E
    # E -> T .
    @args(state_3())
    def test_state_3_entries(self):
        self.assert_state_entries(x, PLUS, EOF)

    # E -> T + . E
    # E -> . T + E
    # E -> . T
    # T -> . x
    @args(state_4())
    def test_state_4_entries(self):
        self.assert_state_entries(x, E, T)

    @args(state_5())
    def test_state_5_entries(self):
        # T -> x .
        self.assert_state_entries(x, PLUS, EOF)

    # E -> T + E .
    @args(state_6())
    def test_state_6_entries(self):
        self.assert_state_entries(x, PLUS, EOF)


class TestLR0GeneratorGenerateActions(TestLR0Generator):
    def subject(self, state, token):
        return self.generator().generate().get(state).get(token)

    def assert_state_actions(self, *state_actions):
        self.assertCountEqual(self.result(), state_actions)

    @args(state_1(), E)
    def test_state_1_token_E(self):
        self.assert_state_actions(shift(state_2()))

    @args(state_1(), T)
    def test_state_1_token_T(self):
        self.assert_state_actions(shift(state_3()))

    @args(state_1(), x)
    def test_state_1_token_x(self):
        self.assert_state_actions(shift(state_5()))

    @args(state_2(), EOF)
    def test_state_2_token_eof(self):
        self.assert_state_actions(accept(grammar.starting_rule))

    @args(state_3(), PLUS)
    def test_state_3_token_plus(self):
        self.assert_state_actions(reduce(rule_3), shift(state_4()))

    @args(state_3(), EOF)
    def test_state_3_token_eof(self):
        self.assert_state_actions(reduce(rule_3))

    @args(state_3(), x)
    def test_state_3_token_x(self):
        self.assert_state_actions(reduce(rule_3))

    @args(state_4(), x)
    def test_state_4_token_x(self):
        self.assert_state_actions(shift(state_5()))

    @args(state_4(), E)
    def test_state_4_token_E(self):
        self.assert_state_actions(shift(state_6()))

    @args(state_4(), T)
    def test_state_4_token_T(self):
        self.assert_state_actions(shift(state_3()))

    @args(state_5(), PLUS)
    def test_state_5_token_plus(self):
        self.assert_state_actions(reduce(rule_4))

    @args(state_5(), EOF)
    def test_state_5_token_eof(self):
        self.assert_state_actions(reduce(rule_4))

    @args(state_5(), x)
    def test_state_5_token_x(self):
        self.assert_state_actions(reduce(rule_4))

    @args(state_6(), EOF)
    def test_state_6_token_eof(self):
        self.assert_state_actions(reduce(rule_2))

    @args(state_6(), PLUS)
    def test_state_6_token_plus(self):
        self.assert_state_actions(reduce(rule_2))

    @args(state_6(), x)
    def test_state_6_token_x(self):
        self.assert_state_actions(reduce(rule_2))

class TestLR0GeneratorGenerateInitialState(TestLR0Generator):
    def subject(self):
        return self.generator().generate().initial_state

    def test_initial_state(self):
        self.assertResult(state_1())


class TestSLRGenerator(TestCase):
    def setUp(self):
        self._generator = SLRGenerator(grammar)

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
    @args(state_1())
    def test_state_1_entries(self):
        self.assert_state_entries(x, E, T)

    # S -> E . $
    @args(state_2())
    def test_state_2_entries(self):
        self.assert_state_entries(EOF)

    # E -> T . + E
    # E -> T .
    @args(state_3())
    def test_state_3_entries(self):
        self.assert_state_entries(PLUS, EOF)

    # E -> T + . E
    # E -> . T + E
    # E -> . T
    # T -> . x
    @args(state_4())
    def test_state_4_entries(self):
        self.assert_state_entries(x, E, T)

    @args(state_5())
    def test_state_5_entries(self):
        # T -> x .
        self.assert_state_entries(PLUS, EOF)

    # E -> T + E .
    @args(state_6())
    def test_state_6_entries(self):
        self.assert_state_entries(EOF)


class TestSLRGeneratorGenerateActions(TestSLRGenerator):
    def subject(self, state, token):
        return self.generator().generate().get(state).get(token)

    def assert_state_actions(self, *state_actions):
        self.assertCountEqual(self.result(), state_actions)

    @args(state_1(), E)
    def test_state_1_token_E(self):
        self.assert_state_actions(shift(state_2()))

    @args(state_1(), T)
    def test_state_1_token_T(self):
        self.assert_state_actions(shift(state_3()))

    @args(state_1(), x)
    def test_state_1_token_x(self):
        self.assert_state_actions(shift(state_5()))

    @args(state_2(), EOF)
    def test_state_2_token_eof(self):
        self.assert_state_actions(accept(grammar.starting_rule))

    @args(state_3(), PLUS)
    def test_state_3_token_plus(self):
        self.assert_state_actions(shift(state_4()))

    @args(state_3(), EOF)
    def test_state_3_token_eof(self):
        self.assert_state_actions(reduce(rule_3))

    @args(state_4(), x)
    def test_state_4_token_x(self):
        self.assert_state_actions(shift(state_5()))

    @args(state_4(), E)
    def test_state_4_token_E(self):
        self.assert_state_actions(shift(state_6()))

    @args(state_4(), T)
    def test_state_4_token_T(self):
        self.assert_state_actions(shift(state_3()))

    @args(state_5(), PLUS)
    def test_state_5_token_plus(self):
        self.assert_state_actions(reduce(rule_4))

    @args(state_5(), EOF)
    def test_state_5_token_eof(self):
        self.assert_state_actions(reduce(rule_4))

    @args(state_6(), EOF)
    def test_state_6_token_eof(self):
        self.assert_state_actions(reduce(rule_2))


class TestSLRGeneratorGenerateInitialState(TestSLRGenerator):
    def subject(self):
        return self.generator().generate().initial_state

    def test_initial_state(self):
        self.assertResult(state_1())
