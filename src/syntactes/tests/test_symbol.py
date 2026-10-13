from unittest_extensions import TestCase, args

from syntactes import Symbol


class TestSymbolAttributes(TestCase):
    def subject(self, name, is_terminal):
        return Symbol(name, is_terminal)

    @args("x", True)
    def test_name(self):
        self.assertEqual(self.result().name, "x")

    @args("x", True)
    def test_is_terminal(self):
        self.assertTrue(self.result().is_terminal)

    @args("E", False)
    def test_is_not_terminal(self):
        self.assertFalse(self.result().is_terminal)

    @args("x", True)
    def test_has_no_value(self):
        self.assertFalse(hasattr(self.result(), "value"))


class TestSymbolEquality(TestCase):
    def subject(self, symbol, other):
        return symbol == other

    @args(Symbol("x", True), Symbol("x", True))
    def test_same_name_and_kind(self):
        self.assertResultTrue()

    @args(Symbol("x", True), Symbol("x", False))
    def test_different_kind(self):
        self.assertResultFalse()

    @args(Symbol("x", True), Symbol("y", True))
    def test_different_name(self):
        self.assertResultFalse()

    @args(Symbol("x", True), "x")
    def test_other_type(self):
        self.assertResultFalse()


class TestSymbolHash(TestCase):
    def subject(self, symbol, other):
        return hash(symbol) == hash(other)

    @args(Symbol("x", True), Symbol("x", True))
    def test_equal_symbols(self):
        self.assertResultTrue()


class TestSymbolStr(TestCase):
    def subject(self, symbol):
        return str(symbol), repr(symbol)

    @args(Symbol("x", True))
    def test_terminal(self):
        self.assertResult(("x", "<Symbol: x>"))

    @args(Symbol.eof())
    def test_eof(self):
        self.assertResult(("$", "<Symbol: $>"))

    @args(Symbol.null())
    def test_null(self):
        self.assertResult(("ε", "<Symbol: ε>"))


class TestSymbolSpecial(TestCase):
    def subject(self, symbol):
        return symbol.is_terminal

    @args(Symbol.eof())
    def test_eof_is_terminal(self):
        self.assertResultTrue()

    @args(Symbol.null())
    def test_null_is_terminal(self):
        self.assertResultTrue()


class TestSymbolLowerThan(TestCase):
    def subject(self, symbol, other):
        return symbol < other

    @args(Symbol("a", True), Symbol("b", True))
    def test_by_name(self):
        self.assertResultTrue()

    @args(Symbol("a", True), "b")
    def test_other_type_raises(self):
        self.assertResultRaises(ValueError)
