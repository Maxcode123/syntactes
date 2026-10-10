import warnings

from unittest_extensions import TestCase, args

from syntactes import Grammar, GrammarError, GrammarWarning, Rule, Token
from syntactes.primitive import (
    Addition,
    Boolean,
    EqualityComparison,
    Float,
    Integer,
    NoneType,
    String,
)

EOF = Token.eof()
START = Token("<start>", False)
expr = Token("expr", False)
term = Token("term", False)
items = Token("items", False)
PLUS = Token("PLUS", True)
NUMBER = Token("NUMBER", True)
COMMA = Token("COMMA", True)
EQ = Token("EQ", True)

EXPR_TEXT = """\
# Sums of numbers.
expr -> expr PLUS term
expr -> term

term -> NUMBER
"""


class TestFromText(TestCase):
    def subject(self, text):
        return Grammar.from_text(text)

    @args(EXPR_TEXT)
    def test_starting_rule_is_added(self):
        self.assertEqual(self.result().starting_rule, Rule(0, START, expr, EOF))

    @args(EXPR_TEXT)
    def test_rules_in_line_order(self):
        self.assertEqual(
            self.result().rules,
            (
                Rule(0, START, expr, EOF),
                Rule(1, expr, expr, PLUS, term),
                Rule(2, expr, term),
                Rule(3, term, NUMBER),
            ),
        )

    @args(EXPR_TEXT)
    def test_rules_numbered_from_zero(self):
        self.assertEqual([rule.number for rule in self.result().rules], [0, 1, 2, 3])

    @args(EXPR_TEXT)
    def test_tokens(self):
        self.assertEqual(self.result().tokens, {START, EOF, expr, term, PLUS, NUMBER})

    @args(EXPR_TEXT)
    def test_terminals(self):
        self.assertEqual(self.result().terminals(), {PLUS, NUMBER})

    @args(EXPR_TEXT.replace("\n", "\r\n"))
    def test_crlf(self):
        self.assertEqual(len(self.result().rules), 4)

    @args("  expr   ->   NUMBER   PLUS  \n")
    def test_extra_whitespace(self):
        self.assertEqual(self.result().rules[1], Rule(1, expr, NUMBER, PLUS))

    @args("expr->NUMBER\n")
    def test_no_whitespace_around_arrow(self):
        self.assertEqual(self.result().rules[1], Rule(1, expr, NUMBER))

    @args("int % expr -> expr PLUS NUMBER\n")
    def test_primitive_not_part_of_symbols(self):
        rule = self.result().rules[1]
        self.assertEqual((rule.lhs, rule.rhs), (expr, (expr, PLUS, NUMBER)))

    @args("items -> items COMMA NUMBER\nitems ->\n")
    def test_empty_rule_without_symbols(self):
        rule = self.result().rules[2]
        self.assertEqual((rule.number, rule.lhs, rule.rhs), (2, items, ()))

    @args("items -> items COMMA NUMBER\nitems -> ε\n")
    def test_empty_rule_with_null(self):
        rule = self.result().rules[2]
        self.assertEqual((rule.number, rule.lhs, rule.rhs), (2, items, ()))

    @args("items -> items COMMA NUMBER\nitems -> ε\n")
    def test_null_not_in_tokens(self):
        self.assertNotIn(Token.null(), self.result().tokens)

    @args("expr -> term\nterm -> NUMBER\n")
    def test_first_lhs_is_start_symbol(self):
        self.assertEqual(self.result().starting_rule.rhs, (expr, EOF))


class TestFromTextPrimitivesMap(TestCase):
    def subject(self, text):
        return dict(Grammar.from_text(text).primitives)

    @args("int % expr -> NUMBER\n")
    def test_int(self):
        self.assertResult({Rule(1, expr, NUMBER): Integer})

    @args("float % expr -> NUMBER\n")
    def test_float(self):
        self.assertResult({Rule(1, expr, NUMBER): Float})

    @args("str % expr -> NUMBER\n")
    def test_str(self):
        self.assertResult({Rule(1, expr, NUMBER): String})

    @args("None % expr -> NUMBER\n")
    def test_none(self):
        self.assertResult({Rule(1, expr, NUMBER): NoneType})

    @args("bool % expr -> NUMBER\n")
    def test_bool(self):
        self.assertResult({Rule(1, expr, NUMBER): Boolean})

    @args("add % expr -> expr PLUS NUMBER\nexpr -> NUMBER\n")
    def test_add(self):
        self.assertResult({Rule(1, expr, expr, PLUS, NUMBER): Addition})

    @args("eq % expr -> NUMBER EQ NUMBER\n")
    def test_eq(self):
        self.assertResult({Rule(1, expr, NUMBER, EQ, NUMBER): EqualityComparison})

    @args(EXPR_TEXT)
    def test_without_primitive(self):
        self.assertResult({})

    @args("int % expr -> expr PLUS term\nexpr -> term\nstr % term -> NUMBER\n")
    def test_mixed(self):
        self.assertResult(
            {
                Rule(1, expr, expr, PLUS, term): Integer,
                Rule(3, term, NUMBER): String,
            }
        )

    @args("expr -> items\nNone % items ->\n")
    def test_empty_rule(self):
        self.assertResult({Rule(2, items): NoneType})


class TestFromTextRoundTrip(TestCase):
    def subject(self, text):
        rules = Grammar.from_text(text).rules[1:]
        return Grammar.from_text("\n".join(map(str, rules)))

    @args("int % expr -> expr PLUS term\nexpr -> term\nNone % term ->\n")
    def test_symbols_read_back_from_str(self):
        self.assertEqual(
            [str(rule) for rule in self.result().rules[1:]],
            ["expr -> expr PLUS term", "expr -> term", "term -> ε"],
        )

    @args("int % expr -> expr PLUS term\nexpr -> term\nNone % term ->\n")
    def test_primitives_not_read_back_from_str(self):
        self.assertEqual(dict(self.result().primitives), {})


ALL = "int, float, str, None, bool, add, sub, mul, div, pow, lt, le, gt, ge, eq, ne"


class TestFromTextErrors(TestCase):
    def subject(self, text):
        return Grammar.from_text(text)

    def assert_problems(self, problems):
        with self.assertRaises(GrammarError) as context:
            self.result()

        self.assertEqual(context.exception.problems, problems)

    @args("")
    def test_empty(self):
        self.assert_problems([(None, "grammar has no rules")])

    @args("# only a comment\n\n")
    def test_only_comments(self):
        self.assert_problems([(None, "grammar has no rules")])

    @args("expr NUMBER\n")
    def test_missing_arrow(self):
        self.assert_problems([(1, "expected 'lhs -> symbols'")])

    @args("-> NUMBER\n")
    def test_missing_lhs(self):
        self.assert_problems([(1, "rule has no left-hand side")])

    @args("my expr -> NUMBER\n")
    def test_lhs_with_space(self):
        self.assert_problems([(1, "invalid left-hand side 'my expr'")])

    @args("9expr -> NUMBER\n")
    def test_invalid_lhs_name(self):
        self.assert_problems([(1, "invalid left-hand side '9expr'")])

    @args("expr -> NUMBER '+' NUMBER\n")
    def test_invalid_symbol(self):
        self.assert_problems([(1, "invalid symbol \"'+'\"")])

    @args("expr -> NUMBER -> NUMBER\n")
    def test_second_arrow(self):
        self.assert_problems([(1, "invalid symbol '->'")])

    @args("expr -> NUMBER $\n")
    def test_eof(self):
        self.assert_problems([(1, "'$' is reserved for the end of the input")])

    @args("expr -> NUMBER ε\n")
    def test_null_with_other_symbols(self):
        self.assert_problems([(1, "ε can only stand alone")])

    @args("expr -> NUMBER\nexpr -> PLUS\nexpr  ->  NUMBER\n")
    def test_duplicate_rule(self):
        self.assert_problems([(3, "duplicate of the rule on line 1")])

    @args("expr ->\nexpr -> ε\n")
    def test_duplicate_empty_rule(self):
        self.assert_problems([(2, "duplicate of the rule on line 1")])

    @args("foo % expr -> NUMBER\n")
    def test_invalid_primitive(self):
        self.assert_problems([(1, f"invalid primitive foo expected one of {ALL}")])

    @args("Integer % expr -> NUMBER\n")
    def test_primitive_class_name(self):
        self.assert_problems([(1, f"invalid primitive Integer expected one of {ALL}")])

    @args("% expr -> NUMBER\n")
    def test_percent_without_primitive(self):
        self.assert_problems([(1, "expected 'primitive % lhs -> symbols'")])

    @args("int % -> NUMBER\n")
    def test_primitive_without_lhs(self):
        self.assert_problems([(1, "rule has no left-hand side")])

    @args("int % 9expr -> NUMBER\n")
    def test_primitive_with_invalid_lhs(self):
        self.assert_problems([(1, "invalid left-hand side '9expr'")])

    @args("int % float % expr -> NUMBER\n")
    def test_two_primitives(self):
        self.assert_problems([(1, "invalid left-hand side 'float % expr'")])

    @args("int % expr -> NUMBER\nfloat % expr -> NUMBER\n")
    def test_duplicate_rule_with_other_primitive(self):
        self.assert_problems([(2, "duplicate of the rule on line 1")])

    @args("expr NUMBER\nexpr -> NUMBER\n9 -> x\nexpr -> $\n")
    def test_all_problems_reported(self):
        self.assert_problems(
            [
                (1, "expected 'lhs -> symbols'"),
                (3, "invalid left-hand side '9'"),
                (4, "'$' is reserved for the end of the input"),
            ]
        )

    @args("expr NUMBER\n")
    def test_message_has_lines(self):
        self.assertResultRaisesRegex(GrammarError, "^line 1: expected")

    @args("expr NUMBER\n")
    def test_is_value_error(self):
        self.assertResultRaises(ValueError)


class TestFromTextWarnings(TestCase):
    def subject(self, text):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Grammar.from_text(text)

        return [
            (w.message.line, w.message.message)
            for w in caught
            if isinstance(w.message, GrammarWarning)
        ]

    @args(EXPR_TEXT)
    def test_no_warnings(self):
        self.assertResult([])

    @args("expr -> NUMBER\nterm -> PLUS\n")
    def test_unreachable(self):
        self.assertResult(
            [(2, "non-terminal 'term' can't be reached from the start symbol 'expr'")]
        )

    @args("expr -> term\nterm -> term PLUS\n")
    def test_unproductive(self):
        self.assertResult(
            [
                (1, "non-terminal 'expr' can't derive a string of terminals"),
                (2, "non-terminal 'term' can't derive a string of terminals"),
            ]
        )

    @args("expr -> NUMBER\n# note\nterm -> items\nitems -> items\nterm -> PLUS\n")
    def test_reported_on_first_lhs_line(self):
        self.assertResult(
            [
                (
                    3,
                    "non-terminal 'term' can't be reached from the start symbol 'expr'",
                ),
                (
                    4,
                    "non-terminal 'items' can't be reached from the start symbol 'expr'",
                ),
                (4, "non-terminal 'items' can't derive a string of terminals"),
            ]
        )

    @args("items -> items COMMA\nitems ->\n")
    def test_empty_rule_is_productive(self):
        self.assertResult([])


class TestGrammarError(TestCase):
    def subject(self, *arguments):
        return GrammarError(*arguments)

    @args("Rule number 1 is used twice.")
    def test_message_only(self):
        self.assertEqual(
            self.result().problems, [(None, "Rule number 1 is used twice.")]
        )

    @args("Rule number 1 is used twice.")
    def test_message_only_str(self):
        self.assertEqual(str(self.result()), "Rule number 1 is used twice.")


class TestGrammarWarning(TestCase):
    def subject(self, line, message):
        return GrammarWarning(line, message)

    @args(3, "something")
    def test_attributes(self):
        self.assertEqual((self.result().line, self.result().message), (3, "something"))

    @args(3, "something")
    def test_str(self):
        self.assertEqual(str(self.result()), "line 3: something")
