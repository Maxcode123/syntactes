from unittest_extensions import TestCase, args

from syntactes import Grammar, LR0Generator, LR1Generator, Rule, SLRGenerator
from syntactes.tests.data import EOF, S, grammar_1, grammar_2, grammar_6, x

SLR_GRAMMAR_1 = """\
GRAMMAR RULES
-------------
0. S -> E $
1. E -> T + E
2. E -> T
3. T -> x
-------------

SLR PARSING TABLE
-------------------------------------------------
|     |  $   |  +   |  E   |  S   |  T   |  x   |
-------------------------------------------------
|  1  |  --  |  --  |  s2  |  --  |  s3  |  s4  |
-------------------------------------------------
|  2  |  a   |  --  |  --  |  --  |  --  |  --  |
-------------------------------------------------
|  3  |  r2  |  s5  |  --  |  --  |  --  |  --  |
-------------------------------------------------
|  4  |  r3  |  r3  |  --  |  --  |  --  |  --  |
-------------------------------------------------
|  5  |  --  |  --  |  s6  |  --  |  s3  |  s4  |
-------------------------------------------------
|  6  |  r1  |  --  |  --  |  --  |  --  |  --  |
-------------------------------------------------
"""


class TestParsingTablePrettyStr(TestCase):
    def subject(self, generator_cls, grammar):
        return generator_cls(grammar).generate().pretty_str()

    def assert_table_lines_aligned(self):
        table = self.result().split("PARSING TABLE\n")[1]
        self.assertEqual(len(set(map(len, table.splitlines()))), 1)

    @args(SLRGenerator, grammar_1)
    def test_slr_grammar_1(self):
        self.assertResult(SLR_GRAMMAR_1)

    # Cells with a conflict hold more than one action.
    @args(LR0Generator, grammar_6)
    def test_lr0_conflicts_aligned(self):
        self.assert_table_lines_aligned()

    # More than nine states.
    @args(LR1Generator, grammar_2)
    def test_lr1_aligned(self):
        self.assert_table_lines_aligned()


class TestParsingTableRuleNumbers(TestCase):
    def subject(self):
        rule = Rule(7, None, S, x, EOF)
        grammar = Grammar(rule, (rule,), {S, x, EOF})
        return SLRGenerator(grammar).generate().pretty_str().splitlines()[2]

    def test_uses_rule_number(self):
        self.assertResult("7. S -> x $")
