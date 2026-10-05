from unittest_extensions import TestCase, args

from syntactes import Token
from syntactes._action import Action
from syntactes.parser import (
    LR0Parser,
    LR1Parser,
    NotAcceptedError,
    ParserError,
    SLRParser,
    UnexpectedTokenError,
)
from syntactes.tests.data import (
    EOF,
    LPAREN,
    NULL,
    PLUS,
    RPAREN,
    E,
    a,
    grammar_1,
    grammar_3,
    grammar_4,
    grammar_6,
    grammar_8,
    lr0_parsing_table,
    lr0_state_1,
    lr1_parsing_table,
    rule_1_1,
    rule_1_3,
    rule_2_1,
    rule_2_6,
    rule_3_1,
    rule_3_4,
    rule_3_6,
    rule_3_8,
    rule_4_1,
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

    def add(self, _left, _plus, _right):
        self.sum += 1

    def setUp(self):
        super().setUp()
        self.sum = 0
        self.parser().execute_on(rule_2_1)(self.add)

    @args(x, PLUS, x, EOF)
    def test_x_plus_x(self):
        self.assertResult(1)

    @args(x, PLUS, x, PLUS, x, EOF)
    def test_x_plus_x_plus_x(self):
        self.assertResult(2)


class TestLR0ParserParseExecutablesTokenValues(TestLR0Parser):
    def subject(self, *stream):
        return self.parser().parse(stream)

    def setUp(self):
        super().setUp()
        self.parser().execute_on(rule_1_1)(lambda e: e.value)
        self.parser().execute_on(rule_2_1)(lambda t, _plus, e: t.value + e.value)
        self.parser().execute_on(rule_3_1)(lambda t: t.value)
        self.parser().execute_on(rule_4_1)(lambda x: x.value)

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

    @args()
    def test_empty_stream_raises(self):
        self.assertResultRaises(NotAcceptedError)

    @args(x, PLUS, x)
    def test_no_eof_raises(self):
        self.assertResultRaises(NotAcceptedError)

    @args(x, EOF, x)
    def test_tokens_after_eof_raise(self):
        self.assertResultRaises(UnexpectedTokenError)

    @args(x, x, EOF)
    def test_x_x_eof_raises(self):
        self.assert_parser_error()

    @args(x, PLUS, x, EOF)
    def test_x_plus_x(self):
        self.result()


class TestLR1Parser(TestCase):
    def parser(self):
        return self._parser

    def setUp(self):
        self._parser = LR1Parser(lr1_parsing_table())

    def assert_parser_error(self):
        self.assertResultRaises(ParserError)


class TestLR1ParserParse(TestLR1Parser):
    def subject(self, *stream):
        return self.parser().parse(stream)

    @args(LPAREN, RPAREN)
    def test_no_eof_raises(self):
        self.assert_parser_error()

    @args(LPAREN, RPAREN, EOF)
    def test_valid_syntax_does_not_raise(self):
        self.result()

    @args(LPAREN, RPAREN, RPAREN, EOF)
    def test_invalid_syntax_raises(self):
        self.assert_parser_error()

    @args(LPAREN, RPAREN, LPAREN, RPAREN, EOF)
    def test_list_of_two(self):
        self.result()


class TestSLRParserWithoutUnitRules(TestCase):
    def subject(self, *stream):
        return SLRParser.from_grammar(grammar_3).parse(stream)

    @args(x, PLUS, x, EOF)
    def test_x_plus_x(self):
        self.result()

    @args(x, EOF)
    def test_x_raises(self):
        self.assertResultRaises(ParserError)


class TestLR1ParserWithoutUnitRules(TestCase):
    def subject(self, *stream):
        return LR1Parser.from_grammar(grammar_3).parse(stream)

    @args(x, PLUS, x, EOF)
    def test_x_plus_x(self):
        self.result()

    @args(x, EOF)
    def test_x_raises(self):
        self.assertResultRaises(ParserError)


class TestParserResolveConflict(TestCase):
    def subject(self, *actions):
        return LR0Parser(lr0_parsing_table())._resolve_conflict(list(actions))

    @args(Action.reduce(rule_3_1), Action.shift(lr0_state_1()))
    def test_shift_over_reduce(self):
        self.assertResult(Action.shift(lr0_state_1()))

    @args(Action.reduce(rule_3_1), Action.reduce(rule_2_1))
    def test_lowest_rule_number(self):
        self.assertResult(Action.reduce(rule_2_1))

    @args(Action.shift(lr0_state_1()), Action.accept())
    def test_accept_over_shift(self):
        self.assertResult(Action.accept())


class TestSLRParserAmbiguousGrammar(TestCase):
    def subject(self, *stream):
        reductions = []
        parser = SLRParser.from_grammar(grammar_6)
        parser.execute_on(rule_2_6)(lambda *_: reductions.append("r"))
        parser.execute_on(rule_3_6)(lambda *_: reductions.append("x"))
        parser.parse(stream)
        return " ".join(reductions)

    @args(x, PLUS, x, PLUS, x, EOF)
    def test_right_associative(self):
        self.assertResult("x x x r r")


class TestSLRParserParseTwice(TestSLRParser):
    def subject(self, first, second):
        try:
            self.parser().parse(first)
        except ParserError:
            pass

        return self.parser().parse(second)

    @args([x, PLUS, x, EOF], [x, EOF])
    def test_after_valid_stream(self):
        self.result()

    @args([x, PLUS, PLUS], [x, EOF])
    def test_after_invalid_stream(self):
        self.result()

    @args([x, PLUS], [x, EOF])
    def test_after_unfinished_stream(self):
        self.result()


class TestSLRParserExpectedTokens(TestSLRParser):
    def subject(self, *stream):
        try:
            self.parser().parse(stream)
        except UnexpectedTokenError as e:
            return e.expected_tokens

    # T -> x . expects + or $
    @args(x, x, EOF)
    def test_terminals_sorted(self):
        self.assertResult([EOF, PLUS])

    # E -> T + . E expects x, not the non-terminals E and T
    @args(x, PLUS, PLUS, EOF)
    def test_without_non_terminals(self):
        self.assertResult([x])


class TestSLRParserReduceArguments(TestSLRParser):
    def subject(self, *stream):
        self.received = []
        self.parser().execute_on(rule_2_1)(lambda *args: self.received.append(args))
        self.parser().parse(stream)
        return [tuple(map(str, args)) for args in self.received]

    @args(x, PLUS, x, EOF)
    def test_rhs_order(self):
        self.assertResult([("T", "+", "E")])


class TestSLRParserValues(TestSLRParser):
    def subject(self, *stream):
        return self.parser().parse(stream)

    def register_evaluator(self):
        self.parser().execute_on(rule_1_1)(lambda e: e.value)
        self.parser().execute_on(rule_2_1)(lambda t, _plus, e: t.value + e.value)
        self.parser().execute_on(rule_3_1)(lambda t: t.value)
        self.parser().execute_on(rule_4_1)(lambda x: x.value)

    @args(x1, PLUS, x2, EOF)
    def test_evaluates_x1_plus_x2(self):
        self.register_evaluator()
        self.assertResult(3)

    @args(x2, PLUS, x2, PLUS, x1, EOF)
    def test_evaluates_x2_plus_x2_plus_x1(self):
        self.register_evaluator()
        self.assertResult(5)

    @args(x1, EOF)
    def test_without_callbacks_returns_none(self):
        self.assertResultIs(None)

    @args(x1, EOF)
    def test_rule_without_callback_has_none_value(self):
        self.parser().execute_on(rule_1_1)(lambda e: ("E", e.value))
        self.assertResult(("E", None))

    @args(x1, PLUS, x2, EOF)
    def test_starting_rule_receives_no_eof(self):
        self.parser().execute_on(rule_1_1)(lambda *args: tuple(map(str, args)))
        self.assertResult(("E",))

    @args(x1, EOF)
    def test_callback_exception_propagates(self):
        self.parser().execute_on(rule_4_1)(lambda x: 1 / 0)
        self.assertResultRaises(ZeroDivisionError)

    @args(x1, EOF)
    def test_grammar_tokens_are_not_mutated(self):
        self.register_evaluator()
        self.result()
        self.assertIsNone(E.value)


class TestParsingTableGrammar(TestCase):
    def subject(self):
        return slr_parsing_table().grammar

    def test_grammar(self):
        self.assertResultIs(grammar_1)


def _callback(*_):
    return None


class TestParserExecuteOn(TestCase):
    def subject(self, rule):
        return SLRParser(slr_parsing_table()).execute_on(rule)(_callback)

    @args(rule_2_1)
    def test_returns_function_unchanged(self):
        self.assertResultIs(_callback)

    # E -> E + E is not a rule of grammar_1
    @args(rule_2_6)
    def test_unknown_rule_raises(self):
        self.assertResultRaises(ValueError)


class TestParserExecutablesArePerParser(TestCase):
    def subject(self):
        parser_1 = SLRParser.from_grammar(grammar_1)
        parser_3 = SLRParser.from_grammar(grammar_3)
        # S -> E $ is a rule of both grammars.
        parser_1.execute_on(rule_1_1)(lambda _e: 1)
        parser_3.execute_on(rule_1_3)(lambda _e: 3)
        return parser_1.parse([x, EOF]), parser_3.parse([x, PLUS, x, EOF])

    def test_callbacks_do_not_leak(self):
        self.assertResult((1, 3))


class TestParserExecutablesAreNotGlobal(TestCase):
    def subject(self):
        SLRParser.from_grammar(grammar_1).execute_on(rule_1_1)(lambda _e: 1)
        return SLRParser.from_grammar(grammar_1).parse([x, EOF])

    def test_other_parser_unaffected(self):
        self.assertResultIs(None)


class TestParserWithEmptyRules(TestCase):
    def subject(self, parser_cls, grammar, *stream):
        return parser_cls.from_grammar(grammar).parse(stream)

    @args(SLRParser, grammar_4, x, EOF)
    def test_slr_without_optional(self):
        self.result()

    @args(SLRParser, grammar_4, a, x, EOF)
    def test_slr_with_optional(self):
        self.result()

    @args(LR1Parser, grammar_4, x, EOF)
    def test_lr1_without_optional(self):
        self.result()

    @args(LR1Parser, grammar_4, a, x, EOF)
    def test_lr1_with_optional(self):
        self.result()

    @args(SLRParser, grammar_8, x, EOF)
    def test_slr_without_null_token(self):
        self.result()

    @args(LR1Parser, grammar_8, a, x, EOF)
    def test_lr1_without_null_token(self):
        self.result()

    @args(SLRParser, grammar_4, a, EOF)
    def test_slr_missing_symbol_raises(self):
        self.assertResultRaises(ParserError)

    @args(LR1Parser, grammar_4, NULL, x, EOF)
    def test_null_token_in_stream_raises(self):
        self.assertResultRaises(ParserError)


class TestParserEmptyRuleCallback(TestCase):
    def subject(self, grammar, rule):
        received = []
        parser = SLRParser.from_grammar(grammar)
        parser.execute_on(rule)(lambda *args: received.append(args))
        parser.parse([x, EOF])
        return received

    @args(grammar_4, rule_3_4)
    def test_with_null_token(self):
        self.assertResult([()])

    @args(grammar_8, rule_3_8)
    def test_without_null_token(self):
        self.assertResult([()])
