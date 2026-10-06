"""
The Python 3.8 grammar, converted from the EBNF of CPython's Grammar/Grammar to
BNF, with a tokenizer and a parser whose callbacks rebuild the source.

f-strings are not covered, because since Python 3.12 the tokenize module splits
them into parts that the 3.8 grammar doesn't know.
"""

import functools
import io
import tokenize as _tokenize
from collections.abc import Callable, Iterator

from syntactes import LR1Generator, Rule, Token
from syntactes.parser import LR1Parser
from syntactes.parsing_table import ParsingTable
from syntactes.tests._bnf import grammar_from_bnf

PYTHON_BNF = """
file_input
    : %empty
    | file_input NEWLINE
    | file_input stmt
    ;
decorator
    : '@' dotted_name NEWLINE
    | '@' dotted_name '(' ')' NEWLINE
    | '@' dotted_name '(' arglist ')' NEWLINE
    ;
decorators : decorator | decorators decorator ;
decorated
    : decorators classdef
    | decorators funcdef
    | decorators async_funcdef
    ;
async_funcdef : 'async' funcdef ;
funcdef
    : 'def' NAME parameters ':' suite
    | 'def' NAME parameters '->' test ':' suite
    ;
parameters : '(' ')' | '(' typedargslist ')' ;
typedargslist : typedargs | typedargs ',' ;
typedargs : typedarg | typedargs ',' typedarg ;
typedarg
    : tfpdef
    | tfpdef '=' test
    | '*'
    | '*' tfpdef
    | '**' tfpdef
    | '/'
    ;
tfpdef : NAME | NAME ':' test ;
varargslist : varargs | varargs ',' ;
varargs : vararg | varargs ',' vararg ;
vararg
    : NAME
    | NAME '=' test
    | '*'
    | '*' NAME
    | '**' NAME
    | '/'
    ;

stmt : simple_stmt | compound_stmt ;
simple_stmt
    : small_stmts NEWLINE
    | small_stmts ';' NEWLINE
    ;
small_stmts : small_stmt | small_stmts ';' small_stmt ;
small_stmt
    : expr_stmt
    | del_stmt
    | pass_stmt
    | flow_stmt
    | import_stmt
    | global_stmt
    | nonlocal_stmt
    | assert_stmt
    ;
expr_stmt
    : testlist_star_expr
    | testlist_star_expr annassign
    | testlist_star_expr augassign yield_expr
    | testlist_star_expr augassign testlist
    | testlist_star_expr assignments
    ;
assignments
    : '=' yield_expr
    | '=' testlist_star_expr
    | assignments '=' yield_expr
    | assignments '=' testlist_star_expr
    ;
annassign
    : ':' test
    | ':' test '=' yield_expr
    | ':' test '=' testlist_star_expr
    ;
testlist_star_expr : test_or_stars | test_or_stars ',' ;
test_or_stars : test_or_star | test_or_stars ',' test_or_star ;
test_or_star : test | star_expr ;
augassign
    : '+=' | '-=' | '*=' | '@=' | '/=' | '%=' | '&=' | '|=' | '^=' | '<<='
    | '>>=' | '**=' | '//='
    ;
del_stmt : 'del' exprlist ;
pass_stmt : 'pass' ;
flow_stmt : break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt ;
break_stmt : 'break' ;
continue_stmt : 'continue' ;
return_stmt : 'return' | 'return' testlist_star_expr ;
yield_stmt : yield_expr ;
raise_stmt : 'raise' | 'raise' test | 'raise' test 'from' test ;
import_stmt : import_name | import_from ;
import_name : 'import' dotted_as_names ;
import_from
    : 'from' dotted_name 'import' import_targets
    | 'from' dots dotted_name 'import' import_targets
    | 'from' dots 'import' import_targets
    ;
dots : '.' | '...' | dots '.' | dots '...' ;
import_targets : '*' | '(' import_as_names ')' | import_as_names ;
import_as_name : NAME | NAME 'as' NAME ;
dotted_as_name : dotted_name | dotted_name 'as' NAME ;
import_as_names : import_as_name_list | import_as_name_list ',' ;
import_as_name_list
    : import_as_name
    | import_as_name_list ',' import_as_name
    ;
dotted_as_names : dotted_as_name | dotted_as_names ',' dotted_as_name ;
dotted_name : NAME | dotted_name '.' NAME ;
global_stmt : 'global' names ;
nonlocal_stmt : 'nonlocal' names ;
names : NAME | names ',' NAME ;
assert_stmt : 'assert' test | 'assert' test ',' test ;

compound_stmt
    : if_stmt
    | while_stmt
    | for_stmt
    | try_stmt
    | with_stmt
    | funcdef
    | classdef
    | decorated
    | async_stmt
    ;
async_stmt : 'async' funcdef | 'async' with_stmt | 'async' for_stmt ;
if_stmt : 'if' namedexpr_test ':' suite elif_clauses else_clause ;
elif_clauses
    : %empty
    | elif_clauses 'elif' namedexpr_test ':' suite
    ;
else_clause : %empty | 'else' ':' suite ;
while_stmt : 'while' namedexpr_test ':' suite else_clause ;
for_stmt : 'for' exprlist 'in' testlist ':' suite else_clause ;
try_stmt
    : 'try' ':' suite except_clauses else_clause finally_clause
    | 'try' ':' suite 'finally' ':' suite
    ;
except_clauses
    : except_clause ':' suite
    | except_clauses except_clause ':' suite
    ;
except_clause : 'except' | 'except' test | 'except' test 'as' NAME ;
finally_clause : %empty | 'finally' ':' suite ;
with_stmt : 'with' with_items ':' suite ;
with_items : with_item | with_items ',' with_item ;
with_item : test | test 'as' expr ;
suite : simple_stmt | NEWLINE INDENT stmts DEDENT ;
stmts : stmt | stmts stmt ;

namedexpr_test : test | test ':=' test ;
test
    : or_test
    | or_test 'if' or_test 'else' test
    | lambdef
    ;
test_nocond : or_test | lambdef_nocond ;
lambdef : 'lambda' ':' test | 'lambda' varargslist ':' test ;
lambdef_nocond
    : 'lambda' ':' test_nocond
    | 'lambda' varargslist ':' test_nocond
    ;
or_test : and_test | or_test 'or' and_test ;
and_test : not_test | and_test 'and' not_test ;
not_test : 'not' not_test | comparison ;
comparison : expr | comparison comp_op expr ;
comp_op
    : '<' | '>' | '==' | '>=' | '<=' | '!=' | 'in' | 'not' 'in' | 'is'
    | 'is' 'not'
    ;
star_expr : '*' expr ;
expr : xor_expr | expr '|' xor_expr ;
xor_expr : and_expr | xor_expr '^' and_expr ;
and_expr : shift_expr | and_expr '&' shift_expr ;
shift_expr
    : arith_expr
    | shift_expr '<<' arith_expr
    | shift_expr '>>' arith_expr
    ;
arith_expr : term | arith_expr '+' term | arith_expr '-' term ;
term
    : factor
    | term '*' factor
    | term '@' factor
    | term '/' factor
    | term '%' factor
    | term '//' factor
    ;
factor : '+' factor | '-' factor | '~' factor | power ;
power : atom_expr | atom_expr '**' factor ;
atom_expr : atom_trailers | 'await' atom_trailers ;
atom_trailers : atom | atom_trailers trailer ;
atom
    : '(' ')'
    | '(' yield_expr ')'
    | '(' testlist_comp ')'
    | '[' ']'
    | '[' testlist_comp ']'
    | '{' '}'
    | '{' dictorsetmaker '}'
    | NAME
    | NUMBER
    | strings
    | '...'
    | 'None'
    | 'True'
    | 'False'
    ;
strings : STRING | strings STRING ;
testlist_comp
    : named_or_star comp_for
    | named_or_stars
    | named_or_stars ','
    ;
named_or_stars : named_or_star | named_or_stars ',' named_or_star ;
named_or_star : namedexpr_test | star_expr ;
trailer
    : '(' ')'
    | '(' arglist ')'
    | '[' subscriptlist ']'
    | '.' NAME
    ;
subscriptlist : subscripts | subscripts ',' ;
subscripts : subscript | subscripts ',' subscript ;
subscript
    : test
    | optional_test ':' optional_test
    | optional_test ':' optional_test ':' optional_test
    ;
optional_test : %empty | test ;
exprlist : expr_or_stars | expr_or_stars ',' ;
expr_or_stars : expr_or_star | expr_or_stars ',' expr_or_star ;
expr_or_star : expr | star_expr ;
testlist : tests | tests ',' ;
tests : test | tests ',' test ;
dictorsetmaker
    : dict_item comp_for
    | dict_items
    | dict_items ','
    | set_item comp_for
    | set_items
    | set_items ','
    ;
dict_items : dict_item | dict_items ',' dict_item ;
dict_item : test ':' test | '**' expr ;
set_items : set_item | set_items ',' set_item ;
set_item : test | star_expr ;

classdef
    : 'class' NAME ':' suite
    | 'class' NAME '(' ')' ':' suite
    | 'class' NAME '(' arglist ')' ':' suite
    ;
arglist : arguments | arguments ',' ;
arguments : argument | arguments ',' argument ;
argument
    : test
    | test comp_for
    | test ':=' test
    | test '=' test
    | '**' test
    | '*' test
    ;
comp_iter : comp_for | comp_if ;
sync_comp_for
    : 'for' exprlist 'in' or_test
    | 'for' exprlist 'in' or_test comp_iter
    ;
comp_for : sync_comp_for | 'async' sync_comp_for ;
comp_if : 'if' test_nocond | 'if' test_nocond comp_iter ;
yield_expr
    : 'yield'
    | 'yield' 'from' test
    | 'yield' testlist_star_expr
    ;
"""

grammar = grammar_from_bnf(PYTHON_BNF, "file_input")


@functools.cache
def parsing_table() -> ParsingTable:
    """
    Returns the LR1 parsing table of the grammar, generated once per test run.
    """
    return LR1Generator(grammar).generate()


# The keywords of Python 3.8, the version of the grammar.
_KEYWORDS = {
    "False", "None", "True", "and", "as", "assert", "async", "await", "break",
    "class", "continue", "def", "del", "elif", "else", "except", "finally", "for",
    "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not",
    "or", "pass", "raise", "return", "try", "while", "with", "yield",
}  # fmt: skip

_SKIPPED = {_tokenize.NL, _tokenize.COMMENT, _tokenize.ENCODING}
# Token types that are terminals of the grammar under their tokenize names.
_NAMED = {
    _tokenize.NUMBER,
    _tokenize.STRING,
    _tokenize.NEWLINE,
    _tokenize.INDENT,
    _tokenize.DEDENT,
}


def tokenize(source: str) -> Iterator[Token]:
    """
    Yields the tokens of the Python source, with the tokenize module's string of
    each as its value, and then the EOF token. Comments and blank lines are
    skipped.

    Raises `ValueError` on an f-string.
    """
    for info in _tokenize.generate_tokens(io.StringIO(source).readline):
        if info.type in _SKIPPED:
            continue

        if info.type == _tokenize.ENDMARKER:
            break

        if info.type == _tokenize.NAME:
            symbol = info.string if info.string in _KEYWORDS else "NAME"
        elif info.type == _tokenize.OP:
            symbol = info.string
        elif info.type in _NAMED:
            symbol = _tokenize.tok_name[info.type]
        else:
            raise ValueError(f"Unsupported token {info}.")

        yield Token(symbol, True, info.string)

    yield Token.eof()


# Rules whose alternatives of more than one symbol are expressions that can be
# put in parentheses without changing the program. Comparisons are left out,
# because a < b < c is a single comparison and (a < b) < c is not.
_EXPRESSIONS = {
    "namedexpr_test", "test", "lambdef", "lambdef_nocond", "or_test", "and_test",
    "not_test", "expr", "xor_expr", "and_expr", "shift_expr", "arith_expr",
    "term", "factor", "power", "atom_expr", "atom_trailers",
}  # fmt: skip

# Stands in for line breaks inside string literals while suites are indented.
_STRING_NEWLINE = ""


def source_parser() -> LR1Parser:
    """
    Returns a parser whose callbacks rebuild the source from the tokens, with
    every expression of more than one symbol in parentheses, so the result
    shows how the parser grouped it. The result is Python source again, and
    parses to the same AST as the original exactly when the grouping matches
    Python's.
    """
    parser = LR1Parser(parsing_table())
    for rule in grammar.rules:
        parser.execute_on(rule)(_source_callback(rule))

    return parser


def _source_callback(rule: Rule) -> Callable[..., str]:
    lhs = rule.lhs.symbol
    if lhs == "<start>":
        return lambda file_input: file_input.value.replace(_STRING_NEWLINE, "\n")

    if lhs == "suite" and rule.rhs_len == 4:
        return lambda _newline, _in, stmts, _out: "\n" + _indent(stmts.value)

    parenthesize = lhs in _EXPRESSIONS and rule.rhs_len > 1

    def callback(*tokens: Token) -> str:
        text = _join(_text(token) for token in tokens)
        return f"({text})" if parenthesize else text

    return callback


def _text(token: Token) -> str:
    if token.symbol == "NEWLINE":
        return "\n"

    value = token.value
    if value is None or token.symbol in ("INDENT", "DEDENT"):
        return ""

    if token.symbol == "STRING":
        return value.replace("\n", _STRING_NEWLINE)

    return value


def _join(texts: Iterator[str]) -> str:
    """
    Joins the texts with spaces, but not at the start of a line.
    """
    joined = ""
    for text in texts:
        if not text:
            continue

        if joined and not joined.endswith("\n") and not text.startswith("\n"):
            joined += " "

        joined += text

    return joined


def _indent(text: str) -> str:
    return "".join(f"    {line}\n" for line in text.split("\n") if line)
