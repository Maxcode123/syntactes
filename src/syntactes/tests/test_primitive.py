from unittest_extensions import TestCase, args

from syntactes.primitive import (
    Addition,
    Boolean,
    Division,
    EqualityComparison,
    Exponentiation,
    Float,
    GreaterEqualThanComparison,
    GreaterThanComparison,
    InequalityComparison,
    Integer,
    LowerEqualThanComparison,
    LowerThanComparison,
    Multiplication,
    NoneType,
    String,
    Subtraction,
    primitives,
)


class TestPrimitiveConversion(TestCase):
    def subject(self, primitive, value):
        return primitive(value)

    @args(Integer, "42")
    def test_integer(self):
        self.assertResult(42)

    @args(Integer, "42")
    def test_integer_type(self):
        self.assertResultIsInstance(int)

    @args(Integer, "4.2")
    def test_integer_invalid(self):
        self.assertResultRaises(ValueError)

    @args(Float, "4.2")
    def test_float(self):
        self.assertResult(4.2)

    @args(Float, "42")
    def test_float_type(self):
        self.assertResultIsInstance(float)

    @args(Float, "x")
    def test_float_invalid(self):
        self.assertResultRaises(ValueError)

    @args(String, 42)
    def test_string(self):
        self.assertResult("42")

    @args(NoneType, "anything")
    def test_none_type(self):
        self.assertResultIs(None)

    @args(Boolean, "true")
    def test_boolean_true(self):
        self.assertResultIs(True)

    @args(Boolean, "1")
    def test_boolean_one(self):
        self.assertResultIs(True)

    @args(Boolean, "false")
    def test_boolean_false(self):
        self.assertResultIs(False)

    @args(Boolean, "0")
    def test_boolean_zero(self):
        self.assertResultIs(False)


class TestPrimitiveOperation(TestCase):
    def subject(self, primitive, left, right):
        return primitive(left, right)

    @args(Addition, 2, 3)
    def test_addition(self):
        self.assertResult(5)

    @args(Addition, 1.5, 2.25)
    def test_addition_float(self):
        self.assertResult(3.75)

    @args(Subtraction, 2, 3)
    def test_subtraction(self):
        self.assertResult(-1)

    @args(Multiplication, 2, 3)
    def test_multiplication(self):
        self.assertResult(6)

    @args(Division, 3, 2)
    def test_division(self):
        self.assertResult(1.5)

    @args(Division, 4, 2)
    def test_division_type(self):
        self.assertResultIsInstance(float)

    @args(Division, 1, 0)
    def test_division_by_zero(self):
        self.assertResultRaises(ZeroDivisionError)

    @args(Exponentiation, 2, 3)
    def test_exponentiation(self):
        self.assertResult(8)

    @args(LowerThanComparison, 2, 3)
    def test_lower_than(self):
        self.assertResultIs(True)

    @args(LowerThanComparison, 3, 3)
    def test_lower_than_equal_operands(self):
        self.assertResultIs(False)

    @args(LowerEqualThanComparison, 3, 3)
    def test_lower_equal_than(self):
        self.assertResultIs(True)

    @args(LowerEqualThanComparison, 4, 3)
    def test_lower_equal_than_greater(self):
        self.assertResultIs(False)

    @args(GreaterThanComparison, 3, 2)
    def test_greater_than(self):
        self.assertResultIs(True)

    @args(GreaterThanComparison, 3, 3)
    def test_greater_than_equal_operands(self):
        self.assertResultIs(False)

    @args(GreaterEqualThanComparison, 3, 3)
    def test_greater_equal_than(self):
        self.assertResultIs(True)

    @args(GreaterEqualThanComparison, 2, 3)
    def test_greater_equal_than_lower(self):
        self.assertResultIs(False)

    @args(EqualityComparison, 3, 3)
    def test_equality(self):
        self.assertResultIs(True)

    @args(EqualityComparison, 3, 4)
    def test_equality_different(self):
        self.assertResultIs(False)

    @args(InequalityComparison, 3, 4)
    def test_inequality(self):
        self.assertResultIs(True)

    @args(InequalityComparison, 3, 3)
    def test_inequality_equal(self):
        self.assertResultIs(False)


class TestPrimitiveString(TestCase):
    def subject(self, primitive):
        return primitive.string()

    @args(Integer)
    def test_integer(self):
        self.assertResult("int")

    @args(Float)
    def test_float(self):
        self.assertResult("float")

    @args(String)
    def test_string(self):
        self.assertResult("str")

    @args(NoneType)
    def test_none_type(self):
        self.assertResult("None")

    @args(Boolean)
    def test_boolean(self):
        self.assertResult("bool")

    @args(Addition)
    def test_addition(self):
        self.assertResult("add")

    @args(Subtraction)
    def test_subtraction(self):
        self.assertResult("sub")

    @args(Multiplication)
    def test_multiplication(self):
        self.assertResult("mul")

    @args(Division)
    def test_division(self):
        self.assertResult("div")

    @args(Exponentiation)
    def test_exponentiation(self):
        self.assertResult("pow")

    @args(LowerThanComparison)
    def test_lower_than(self):
        self.assertResult("lt")

    @args(LowerEqualThanComparison)
    def test_lower_equal_than(self):
        self.assertResult("le")

    @args(GreaterThanComparison)
    def test_greater_than(self):
        self.assertResult("gt")

    @args(GreaterEqualThanComparison)
    def test_greater_equal_than(self):
        self.assertResult("ge")

    @args(EqualityComparison)
    def test_equality(self):
        self.assertResult("eq")

    @args(InequalityComparison)
    def test_inequality(self):
        self.assertResult("ne")


class TestPrimitives(TestCase):
    def subject(self):
        return primitives()

    def test_in_definition_order(self):
        self.assertResult(
            (
                Integer,
                Float,
                String,
                NoneType,
                Boolean,
                Addition,
                Subtraction,
                Multiplication,
                Division,
                Exponentiation,
                LowerThanComparison,
                LowerEqualThanComparison,
                GreaterThanComparison,
                GreaterEqualThanComparison,
                EqualityComparison,
                InequalityComparison,
            )
        )

    def test_names_are_unique(self):
        names = [primitive.string() for primitive in self.result()]
        self.assertEqual(len(names), len(set(names)))

    def test_returns_a_tuple(self):
        self.assertIsInstance(self.result(), tuple)
