from unittest_extensions import TestCase, args

from syntactes import Token
from syntactes.parser import (
    ExecutablesRegistry,
    LR0Parser,
    ParserError,
    SLRParser,
    execute_on,
)
from syntactes.tests.data import (
    EOF,
    PLUS,
    lr0_parsing_table,
    rule_2,
    rule_4,
    slr_parsing_table,
    x,
)

x1 = Token("x", True, 1)
x2 = Token("x", True, 2)


class TestLR0Parser(TestCase):
    def parser(self):
        return self._parser

    def setUp(self):
        self._parser = LR0Parser(lr0_parsing_table())

    def assert_parser_error(self):
        self.assertResultRaises(ParserError)


class TestLR0ParserParse(TestLR0Parser):
    def subject(self, *stream):
        return self.parser().parse(stream)

    @args(x, EOF)
    def test_simple_x(self):
        self.result()

    @args(x, PLUS, x, EOF)
    def test_x_plus_x(self):
        self.result()

    @args(x)
    def test_no_eof_raises(self):
        self.assert_parser_error()

    @args(x, x)
    def test_x_x_raises(self):
        self.assert_parser_error()

    @args(x, PLUS)
    def test_x_plus_raises(self):
        self.assert_parser_error()

    @args(x, PLUS, EOF)
    def test_x_plus_eof_raises(self):
        self.assert_parser_error()

    @args(EOF)
    def test_eof_raises(self):
        self.assert_parser_error()


class TestLR0ParserParseExecutables(TestLR0Parser):
    def subject(self, *stream):
        self.parser().parse(stream)
        return self.sum

    def add(self, _right, _plus, _left):
        self.sum += 1

    def setUp(self):
        self.sum = 0
        self.add = execute_on(rule_2)(self.add)
        super().setUp()

    @args(x, PLUS, x, EOF)
    def test_x_plus_x(self):
        self.assertResult(1)

    @args(x, PLUS, x, PLUS, x, EOF)
    def test_x_plus_x_plus_x(self):
        self.assertResult(2)


class TestLR0ParserParseExecutablesTokenValues(TestLR0Parser):
    def subject(self, *stream):
        self.parser().parse(stream)
        return self.sum

    def push(self, x):
        self.stack.append(x.value)

    def add(self, x1, _plus, x2):
        self.sum = self.stack.pop() + self.stack.pop()

    def setUp(self):
        self.sum = 0
        self.stack = list()
        execute_on(rule_4)(self.push)
        execute_on(rule_2)(self.add)
        super().setUp()

    def tearDown(self):
        ExecutablesRegistry.clear()

    @args(x1, PLUS, x1, EOF)
    def test_x1_plus_x1(self):
        self.assertResult(2)

    @args(x1, PLUS, x2, EOF)
    def test_x1_plus_x2(self):
        self.assertResult(3)

    @args(x2, PLUS, x2, EOF)
    def test_x2_plus_x2(self):
        self.assertResult(4)


class TestSLRParser(TestCase):
    def parser(self):
        return self._parser

    def setUp(self):
        self._parser = SLRParser(slr_parsing_table())

    def assert_parser_error(self):
        self.assertResultRaises(ParserError)


class TestSLRParserParse(TestSLRParser):
    def subject(self, *stream):
        return self.parser().parse(stream)

    @args(x, x, EOF)
    def test_x_x_eof_raises(self):
        self.assert_parser_error()

    @args(x, PLUS, x, EOF)
    def test_x_plus_x(self):
        self.result()
