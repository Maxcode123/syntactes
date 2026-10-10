from unittest_extensions import TestCase, args

from syntactes import Rule
from syntactes.tests.data import NULL, A, a


class TestRuleIsEmpty(TestCase):
    def subject(self, *rhs):
        return Rule(0, A, *rhs).is_empty()

    @args()
    def test_without_symbols(self):
        self.assertResultTrue()

    @args(NULL)
    def test_with_null(self):
        self.assertResultTrue()

    @args(a)
    def test_with_symbol(self):
        self.assertResultFalse()


class TestRuleStr(TestCase):
    def subject(self, *rhs):
        return str(Rule(0, A, *rhs))

    @args()
    def test_without_symbols(self):
        self.assertResult("A -> ε")

    @args(NULL)
    def test_with_null(self):
        self.assertResult("A -> ε")

    @args(a, A)
    def test_with_symbols(self):
        self.assertResult("A -> a A")


class TestRuleHasNoPrimitive(TestCase):
    def subject(self):
        return Rule(0, A, a)

    def test_no_primitive_attribute(self):
        self.assertFalse(hasattr(self.result(), "primitive"))
