from unittest_extensions import TestCase, args

from syntactes import Symbol, Token

x = Symbol("x", True)
y = Symbol("y", True)


class TestTokenAttributes(TestCase):
    def subject(self, *args):
        return Token(*args)

    @args(x, 1)
    def test_symbol(self):
        self.assertIs(self.result().symbol, x)

    @args(x, 1)
    def test_value(self):
        self.assertEqual(self.result().value, 1)

    @args(x)
    def test_value_defaults_to_none(self):
        self.assertIsNone(self.result().value)


class TestTokenEquality(TestCase):
    def subject(self, token, other):
        return token == other

    @args(Token(x, 1), Token(x, 1))
    def test_same_symbol_and_value(self):
        self.assertResultTrue()

    @args(Token(x, 1), Token(x, 2))
    def test_different_value(self):
        self.assertResultFalse()

    @args(Token(x, 1), Token(y, 1))
    def test_different_symbol(self):
        self.assertResultFalse()

    @args(Token(x), x)
    def test_symbol_is_not_a_token(self):
        self.assertResultFalse()


class TestTokenHash(TestCase):
    def subject(self, token):
        return hash(token)

    @args(Token(x, [1]))
    def test_unhashable_value(self):
        self.assertResult(hash(Token(x, [2])))


class TestTokenStr(TestCase):
    def subject(self, token):
        return str(token), repr(token)

    @args(Token(x, 1))
    def test_with_value(self):
        self.assertResult(("x", "<Token: x, 1>"))

    @args(Token(Symbol.eof()))
    def test_eof(self):
        self.assertResult(("$", "<Token: $, None>"))
