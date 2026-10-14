from types import SimpleNamespace

from unittest_extensions import TestCase, args

from syntactes import Symbol, Token
from syntactes.parser import Location, LocationObjectError

x = Symbol("x", True)
y = Symbol("y", True)
loc = Location(0, 1, 1)


class TestTokenAttributes(TestCase):
    def subject(self, *args):
        return Token(*args)

    @args(x, loc, 1)
    def test_symbol(self):
        self.assertIs(self.result().symbol, x)

    @args(x, loc, 1)
    def test_location(self):
        self.assertIs(self.result().location, loc)

    @args(x, loc, 1)
    def test_value(self):
        self.assertEqual(self.result().value, 1)

    @args(x, loc)
    def test_value_defaults_to_none(self):
        self.assertIsNone(self.result().value)


class TestTokenEquality(TestCase):
    def subject(self, token, other):
        return token == other

    @args(Token(x, loc, 1), Token(x, loc, 1))
    def test_same_symbol_and_value(self):
        self.assertResultTrue()

    @args(Token(x, loc, 1), Token(x, loc, 2))
    def test_different_value(self):
        self.assertResultFalse()

    @args(Token(x, loc, 1), Token(y, loc, 1))
    def test_different_symbol(self):
        self.assertResultFalse()

    @args(Token(x, loc), x)
    def test_symbol_is_not_a_token(self):
        self.assertResultFalse()


class TestTokenHash(TestCase):
    def subject(self, token):
        return hash(token)

    @args(Token(x, loc, [1]))
    def test_unhashable_value(self):
        self.assertResult(hash(Token(x, loc, [2])))


class TestTokenStr(TestCase):
    def subject(self, token):
        return str(token), repr(token)

    @args(Token(x, loc, 1))
    def test_with_value(self):
        self.assertResult(("x", "<Token: x, 1>"))

    @args(Token(Symbol.eof(), loc))
    def test_eof(self):
        self.assertResult(("$", "<Token: $, None>"))


class TestLocationFromObject(TestCase):
    def subject(self, obj):
        return Location.from_object(obj)

    def assert_error_names(self, name):
        with self.assertRaises(LocationObjectError) as cm:
            self.result()
        self.assertIn(repr(name), str(cm.exception))

    def assert_cause(self, cause_type):
        with self.assertRaises(LocationObjectError) as cm:
            self.result()
        self.assertIsInstance(cm.exception.__cause__, cause_type)

    @args({"offset": 4, "line": 2, "column": 3})
    def test_mapping(self):
        self.assertResult(Location(4, 2, 3))

    @args(SimpleNamespace(offset=4, line=2, column=3))
    def test_attributes(self):
        self.assertResult(Location(4, 2, 3))

    @args(Location(4, 2, 3))
    def test_location(self):
        self.assertResult(Location(4, 2, 3))

    @args({"offset": 4, "line": 2, "column": 3, "text": "x"})
    def test_mapping_extra_keys_are_ignored(self):
        self.assertResult(Location(4, 2, 3))

    @args(SimpleNamespace(offset=4, line=2, column=3, text="x"))
    def test_extra_attributes_are_ignored(self):
        self.assertResult(Location(4, 2, 3))

    @args({"offset": 4, "column": 3})
    def test_mapping_missing_key_raises(self):
        self.assert_error_names("line")

    @args(SimpleNamespace(offset=4, line=2))
    def test_missing_attribute_raises(self):
        self.assert_error_names("column")

    @args({})
    def test_mapping_reports_first_missing_key(self):
        self.assert_error_names("offset")

    @args({"offset": 4, "line": "two", "column": 3})
    def test_mapping_non_integer_raises(self):
        self.assert_error_names("line")

    @args(SimpleNamespace(offset=4, line=2, column=None))
    def test_non_integer_attribute_raises(self):
        self.assert_error_names("column")

    @args({"offset": 4, "line": "two", "column": 3})
    def test_mapping_conversion_error_is_cause(self):
        self.assert_cause(ValueError)

    @args(SimpleNamespace(offset=4, line=2, column=None))
    def test_attribute_conversion_error_is_cause(self):
        self.assert_cause(TypeError)

    @args(None)
    def test_object_without_attributes_raises(self):
        self.assertResultRaises(LocationObjectError)


class TestLocation(TestCase):
    def subject(self, location):
        return location

    @args(Location(4, 2, 3))
    def test_hashable(self):
        self.assertEqual(hash(self.result()), hash(Location(4, 2, 3)))

    @args(Location(4, 2, 3))
    def test_immutable(self):
        with self.assertRaises(AttributeError):
            self.result().line = 5
