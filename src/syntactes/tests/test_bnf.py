from unittest_extensions import TestCase, args

from syntactes import Rule, Symbol
from syntactes.tests._bnf import find_rule, grammar_from_bnf

LIST_BNF = """
# A comma separated list, possibly empty.
list
    : %empty
    | items
    ;
items : ITEM | items ',' ITEM ;
"""


class TestGrammarFromBnf(TestCase):
    def subject(self, bnf, start):
        return grammar_from_bnf(bnf, start)

    def assert_rules(self, *rules):
        self.assertEqual(list(map(str, self.result().rules)), list(rules))

    @args(LIST_BNF, "list")
    def test_rules(self):
        self.assert_rules(
            "<start> -> list $",
            "list -> ε",
            "list -> items",
            "items -> ITEM",
            "items -> items , ITEM",
        )

    @args(LIST_BNF, "list")
    def test_rule_numbers(self):
        self.assertEqual([r.number for r in self.result().rules], [0, 1, 2, 3, 4])

    @args(LIST_BNF, "list")
    def test_quoted_terminal(self):
        self.assertIn(Symbol(",", True), self.result().symbols)

    @args(LIST_BNF, "list")
    def test_unquoted_terminal(self):
        self.assertIn(Symbol("ITEM", True), self.result().symbols)

    @args(LIST_BNF, "list")
    def test_non_terminal(self):
        self.assertIn(Symbol("items", False), self.result().symbols)

    @args("a : b ;", "a")
    def test_undefined_non_terminal_raises(self):
        self.assertResultRaises(ValueError)

    @args("a : B", "a")
    def test_unterminated_definition_raises(self):
        self.assertResultRaises(ValueError)


class TestFindRule(TestCase):
    def subject(self, *words):
        return find_rule(grammar_from_bnf(LIST_BNF, "list"), *words)

    @args("items", "items", "','", "ITEM")
    def test_finds_rule(self):
        self.assertResult(
            Rule(
                4,
                Symbol("items", False),
                Symbol("items", False),
                Symbol(",", True),
                Symbol("ITEM", True),
            )
        )

    @args("list")
    def test_finds_empty_rule(self):
        self.assertResult(Rule(1, Symbol("list", False)))

    @args("items", "ITEM", "ITEM")
    def test_missing_rule_raises(self):
        self.assertResultRaises(LookupError)
