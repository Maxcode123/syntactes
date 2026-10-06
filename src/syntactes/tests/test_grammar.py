from unittest_extensions import TestCase, args

from syntactes import Grammar, GrammarError, Rule
from syntactes.tests import data
from syntactes.tests.data import EOF, NULL, PLUS, A, E, S, T, a, x

valid_rules = (Rule(0, S, E, EOF), Rule(1, E, T, PLUS, E), Rule(2, T, x))
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
