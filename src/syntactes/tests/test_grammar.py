import copy
import pickle

from unittest_extensions import TestCase, args

from syntactes import Grammar, GrammarError, Rule
from syntactes.primitive import Addition, Integer, NoneType, Subtraction
from syntactes.tests import data
from syntactes.tests.data import EOF, NULL, PLUS, A, E, S, T, a, x

valid_rules = (
    Rule(0, S, E, EOF),
    Rule(1, E, T, PLUS, E),
    Rule(2, T, x),
)
valid_tokens = {EOF, S, E, T, x, PLUS}


class TestGrammar(TestCase):
    def subject(self, starting_rule, rules, tokens):
        return Grammar(starting_rule, rules, tokens)

    def assert_grammar_error(self):
        self.assertResultRaises(GrammarError)

    @args(valid_rules[0], valid_rules, valid_tokens)
    def test_valid_grammar(self):
        self.assertResultIsInstance(Grammar)

    @args(valid_rules[0], iter(valid_rules), valid_tokens)
    def test_rules_iterable_stored_as_tuple(self):
        self.assertEqual(self.result().rules, valid_rules)

    @args(Rule(0, S, E, EOF), valid_rules[1:], valid_tokens)
    def test_starting_rule_not_in_rules(self):
        self.assert_grammar_error()

    @args(Rule(0, S, E), (Rule(0, S, E), *valid_rules[1:]), valid_tokens)
    def test_starting_rule_without_eof(self):
        self.assert_grammar_error()

    @args(
        Rule(0, S, E, EOF, EOF),
        (Rule(0, S, E, EOF, EOF), *valid_rules[1:]),
        valid_tokens,
    )
    def test_eof_twice_in_starting_rule(self):
        self.assert_grammar_error()

    @args(valid_rules[0], (*valid_rules, Rule(3, T, x, EOF)), valid_tokens)
    def test_eof_in_other_rule(self):
        self.assert_grammar_error()

    @args(valid_rules[0], (*valid_rules, Rule(3, x, T)), valid_tokens)
    def test_terminal_lhs(self):
        self.assert_grammar_error()

    @args(valid_rules[0], (*valid_rules, Rule(3, T, a)), valid_tokens)
    def test_undeclared_rhs_symbol(self):
        self.assert_grammar_error()

    @args(valid_rules[0], (*valid_rules, Rule(3, A, x)), valid_tokens | {T})
    def test_undeclared_lhs_symbol(self):
        self.assert_grammar_error()

    @args(valid_rules[0], (*valid_rules, Rule(3, T, NULL)), valid_tokens)
    def test_undeclared_null_allowed(self):
        self.assertResultIsInstance(Grammar)

    @args(valid_rules[0], valid_rules[:2], valid_tokens)
    def test_non_terminal_without_rules(self):
        self.assert_grammar_error()

    @args(valid_rules[0], (*valid_rules, Rule(2, T, PLUS)), valid_tokens)
    def test_duplicate_rule_numbers(self):
        self.assert_grammar_error()


class TestGrammarPrimitives(TestCase):
    def subject(self, primitives):
        return Grammar(valid_rules[0], valid_rules, valid_tokens, primitives=primitives)

    @args(None)
    def test_empty_by_default(self):
        self.assertEqual(dict(self.result().primitives), {})

    @args({valid_rules[2]: Integer})
    def test_stored(self):
        self.assertEqual(dict(self.result().primitives), {valid_rules[2]: Integer})

    def test_copied_from_argument(self):
        primitives = {valid_rules[2]: Integer}
        grammar = Grammar(
            valid_rules[0], valid_rules, valid_tokens, primitives=primitives
        )
        primitives[valid_rules[1]] = Addition
        self.assertEqual(dict(grammar.primitives), {valid_rules[2]: Integer})

    @args({valid_rules[2]: Integer})
    def test_read_only(self):
        with self.assertRaises(TypeError):
            self.result().primitives[valid_rules[1]] = Addition

    @args({Rule(3, T, PLUS): Integer})
    def test_rule_not_in_rules(self):
        self.assertResultRaises(GrammarError)

    @args({Rule(99, T, x): Integer})
    def test_rule_matched_by_symbols(self):
        self.assertEqual(dict(self.result().primitives), {valid_rules[2]: Integer})

    @args({valid_rules[2]: int})
    def test_builtin_type_value(self):
        self.assertResultRaises(GrammarError)

    @args({valid_rules[2]: lambda value: value})
    def test_function_value(self):
        self.assertResultRaises(GrammarError)

    @args({valid_rules[0]: NoneType})
    def test_starting_rule_allowed(self):
        self.assertEqual(dict(self.result().primitives), {valid_rules[0]: NoneType})

    def test_keyword_only(self):
        with self.assertRaises(TypeError):
            Grammar(valid_rules[0], valid_rules, valid_tokens, {})  # ty: ignore[too-many-positional-arguments]

    @args({valid_rules[2]: Integer})
    def test_pickle_round_trip(self):
        grammar = pickle.loads(pickle.dumps(self.result()))
        self.assertEqual(dict(grammar.primitives), {valid_rules[2]: Integer})

    @args({valid_rules[2]: Integer})
    def test_deepcopy(self):
        grammar = copy.deepcopy(self.result())
        self.assertEqual(dict(grammar.primitives), {valid_rules[2]: Integer})

    @args({valid_rules[2]: Integer})
    def test_deepcopy_still_read_only(self):
        with self.assertRaises(TypeError):
            copy.deepcopy(self.result()).primitives[valid_rules[1]] = Addition


sum_rule = valid_rules[1]
x_rule = valid_rules[2]


class TestGrammarOperands(TestCase):
    def subject(self, primitives, operands):
        return Grammar(
            valid_rules[0],
            valid_rules,
            valid_tokens,
            primitives=primitives,
            operands=operands,
        )

    @args(None, None)
    def test_empty_by_default(self):
        self.assertEqual(dict(self.result().operands), {})

    @args({sum_rule: Addition}, {sum_rule: (1, 3)})
    def test_stored(self):
        self.assertEqual(dict(self.result().operands), {sum_rule: (1, 3)})

    @args({sum_rule: Subtraction}, {sum_rule: (3, 1)})
    def test_order_kept(self):
        self.assertEqual(dict(self.result().operands), {sum_rule: (3, 1)})

    @args({sum_rule: Addition}, None)
    def test_default_first_and_last(self):
        self.assertEqual(dict(self.result().operands), {sum_rule: (1, 3)})

    @args({x_rule: Integer}, None)
    def test_value_type_absent(self):
        self.assertEqual(dict(self.result().operands), {})

    @args({sum_rule: Addition}, {Rule(99, E, T, PLUS, E): (1, 3)})
    def test_rule_matched_by_symbols(self):
        self.assertEqual(dict(self.result().operands), {sum_rule: (1, 3)})

    @args({sum_rule: Addition}, {sum_rule: (1, 3)})
    def test_read_only(self):
        with self.assertRaises(TypeError):
            self.result().operands[sum_rule] = (3, 1)

    @args({sum_rule: Addition}, {sum_rule: (1, 3)})
    def test_pickle_round_trip(self):
        grammar = pickle.loads(pickle.dumps(self.result()))
        self.assertEqual(dict(grammar.operands), {sum_rule: (1, 3)})

    @args({sum_rule: Addition}, {sum_rule: (1, 3)})
    def test_deepcopy(self):
        grammar = copy.deepcopy(self.result())
        self.assertEqual(dict(grammar.operands), {sum_rule: (1, 3)})

    @args({sum_rule: Addition}, {Rule(9, E, T, T): (1, 2)})
    def test_rule_not_in_rules(self):
        self.assertResultRaises(GrammarError)

    @args(None, {sum_rule: (1, 3)})
    def test_rule_without_primitive(self):
        self.assertResultRaises(GrammarError)

    @args({sum_rule: Integer}, {sum_rule: (1, 3)})
    def test_value_type_rule(self):
        self.assertResultRaises(GrammarError)

    @args({sum_rule: Addition}, {sum_rule: (1, 4)})
    def test_position_too_high(self):
        self.assertResultRaises(GrammarError)

    @args({sum_rule: Addition}, {sum_rule: (0, 3)})
    def test_position_zero(self):
        self.assertResultRaises(GrammarError)

    @args({sum_rule: Addition}, {sum_rule: (2, 2)})
    def test_equal_positions(self):
        self.assertResultRaises(GrammarError)

    @args({x_rule: Addition}, None)
    def test_binary_with_one_symbol(self):
        self.assertResultRaises(GrammarError)


class TestGrammarErrorIsValueError(TestCase):
    def subject(self):
        return GrammarError("")

    def test_is_value_error(self):
        self.assertResultIsInstance(ValueError)


class TestTestGrammarsAreValid(TestCase):
    def subject(self, grammar):
        return Grammar(grammar.starting_rule, grammar.rules, grammar.tokens)

    @args(data.grammar_1)
    def test_grammar_1(self):
        self.result()

    @args(data.grammar_2)
    def test_grammar_2(self):
        self.result()

    @args(data.grammar_4)
    def test_grammar_4(self):
        self.result()

    @args(data.grammar_7)
    def test_grammar_7(self):
        self.result()

    @args(data.grammar_8)
    def test_grammar_8(self):
        self.result()
