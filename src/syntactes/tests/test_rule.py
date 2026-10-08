from unittest_extensions import TestCase, args

from syntactes import Rule
from syntactes.primitive import Float, Integer, NoneType, String
from syntactes.tests.data import NULL, A, a


class TestRuleIsEmpty(TestCase):
    def subject(self, *rhs):
        return Rule(0, None, A, *rhs).is_empty()

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
        return str(Rule(0, None, A, *rhs))

    @args()
    def test_without_symbols(self):
        self.assertResult("A -> ε")

    @args(NULL)
    def test_with_null(self):
        self.assertResult("A -> ε")

    @args(a, A)
    def test_with_symbols(self):
        self.assertResult("A -> a A")


class TestRuleStrWithPrimitive(TestCase):
    def subject(self, primitive):
        return str(Rule(0, primitive, A, a, A))

    @args(Integer)
    def test_int(self):
        self.assertResult("int % A -> a A")

    @args(Float)
    def test_float(self):
        self.assertResult("float % A -> a A")

    @args(String)
    def test_str(self):
        self.assertResult("str % A -> a A")

    @args(NoneType)
    def test_none(self):
        self.assertResult("None % A -> a A")


class TestRuleStrEmptyWithPrimitive(TestCase):
    def subject(self, *rhs):
        return str(Rule(0, NoneType, A, *rhs))

    @args()
    def test_without_symbols(self):
        self.assertResult("None % A -> ε")

    @args(NULL)
    def test_with_null(self):
        self.assertResult("None % A -> ε")


class TestRulePrimitive(TestCase):
    def subject(self, primitive):
        return Rule(0, primitive, A, a).primitive

    @args(None)
    def test_none_by_default(self):
        self.assertResultIs(None)

    @args(Integer)
    def test_stored(self):
        self.assertResultIs(Integer)
