from unittest_extensions import TestCase, args

from syntactes.primitive import Float, Integer, NoneType, String


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
