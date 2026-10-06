"""
The ANSI C (C89) grammar, as given by the yacc grammar that accompanied the
standard, with a lexer and a parser whose callbacks rebuild the source.

Telling typedef names from identifiers needs the symbol table (the "lexer hack"),
so the lexer is given the typedef names of the source up front. C requires a
typedef to be declared before it is used, so a typedef name is an identifier at
its first occurrence other than as a struct, union or enum tag (the declaration
itself) and a type name after that.
"""

import functools
import re
from collections.abc import Callable, Collection, Iterator

from syntactes import LR1Generator, Rule, Token
from syntactes.parser import LR1Parser
from syntactes.parsing_table import ParsingTable
from syntactes.tests._bnf import grammar_from_bnf

C_BNF = """
primary_expression
    : IDENTIFIER
    | CONSTANT
    | STRING_LITERAL
    | '(' expression ')'
    ;
postfix_expression
    : primary_expression
    | postfix_expression '[' expression ']'
    | postfix_expression '(' ')'
    | postfix_expression '(' argument_expression_list ')'
    | postfix_expression '.' IDENTIFIER
    | postfix_expression PTR_OP IDENTIFIER
    | postfix_expression INC_OP
    | postfix_expression DEC_OP
    ;
argument_expression_list
    : assignment_expression
    | argument_expression_list ',' assignment_expression
    ;
unary_expression
    : postfix_expression
    | INC_OP unary_expression
    | DEC_OP unary_expression
    | unary_operator cast_expression
    | SIZEOF unary_expression
    | SIZEOF '(' type_name ')'
    ;
unary_operator : '&' | '*' | '+' | '-' | '~' | '!' ;
cast_expression
    : unary_expression
    | '(' type_name ')' cast_expression
    ;
multiplicative_expression
    : cast_expression
    | multiplicative_expression '*' cast_expression
    | multiplicative_expression '/' cast_expression
    | multiplicative_expression '%' cast_expression
    ;
additive_expression
    : multiplicative_expression
    | additive_expression '+' multiplicative_expression
    | additive_expression '-' multiplicative_expression
    ;
shift_expression
    : additive_expression
    | shift_expression LEFT_OP additive_expression
    | shift_expression RIGHT_OP additive_expression
    ;
relational_expression
    : shift_expression
    | relational_expression '<' shift_expression
    | relational_expression '>' shift_expression
    | relational_expression LE_OP shift_expression
    | relational_expression GE_OP shift_expression
    ;
equality_expression
    : relational_expression
    | equality_expression EQ_OP relational_expression
    | equality_expression NE_OP relational_expression
    ;
and_expression
    : equality_expression
    | and_expression '&' equality_expression
    ;
exclusive_or_expression
    : and_expression
    | exclusive_or_expression '^' and_expression
    ;
inclusive_or_expression
    : exclusive_or_expression
    | inclusive_or_expression '|' exclusive_or_expression
    ;
logical_and_expression
    : inclusive_or_expression
    | logical_and_expression AND_OP inclusive_or_expression
    ;
logical_or_expression
    : logical_and_expression
    | logical_or_expression OR_OP logical_and_expression
    ;
conditional_expression
    : logical_or_expression
    | logical_or_expression '?' expression ':' conditional_expression
    ;
assignment_expression
    : conditional_expression
    | unary_expression assignment_operator assignment_expression
    ;
assignment_operator
    : '=' | MUL_ASSIGN | DIV_ASSIGN | MOD_ASSIGN | ADD_ASSIGN | SUB_ASSIGN
    | LEFT_ASSIGN | RIGHT_ASSIGN | AND_ASSIGN | XOR_ASSIGN | OR_ASSIGN
    ;
expression
    : assignment_expression
    | expression ',' assignment_expression
    ;
constant_expression : conditional_expression ;

declaration
    : declaration_specifiers ';'
    | declaration_specifiers init_declarator_list ';'
    ;
declaration_specifiers
    : storage_class_specifier
    | storage_class_specifier declaration_specifiers
    | type_specifier
    | type_specifier declaration_specifiers
    | type_qualifier
    | type_qualifier declaration_specifiers
    ;
init_declarator_list
    : init_declarator
    | init_declarator_list ',' init_declarator
    ;
init_declarator
    : declarator
    | declarator '=' initializer
    ;
storage_class_specifier : TYPEDEF | EXTERN | STATIC | AUTO | REGISTER ;
type_specifier
    : VOID | CHAR | SHORT | INT | LONG | FLOAT | DOUBLE | SIGNED | UNSIGNED
    | struct_or_union_specifier
    | enum_specifier
    | TYPE_NAME
    ;
struct_or_union_specifier
    : struct_or_union IDENTIFIER '{' struct_declaration_list '}'
    | struct_or_union '{' struct_declaration_list '}'
    | struct_or_union IDENTIFIER
    ;
struct_or_union : STRUCT | UNION ;
struct_declaration_list
    : struct_declaration
    | struct_declaration_list struct_declaration
    ;
struct_declaration : specifier_qualifier_list struct_declarator_list ';' ;
specifier_qualifier_list
    : type_specifier specifier_qualifier_list
    | type_specifier
    | type_qualifier specifier_qualifier_list
    | type_qualifier
    ;
struct_declarator_list
    : struct_declarator
    | struct_declarator_list ',' struct_declarator
    ;
struct_declarator
    : declarator
    | ':' constant_expression
    | declarator ':' constant_expression
    ;
enum_specifier
    : ENUM '{' enumerator_list '}'
    | ENUM IDENTIFIER '{' enumerator_list '}'
    | ENUM IDENTIFIER
    ;
enumerator_list
    : enumerator
    | enumerator_list ',' enumerator
    ;
enumerator
    : IDENTIFIER
    | IDENTIFIER '=' constant_expression
    ;
type_qualifier : CONST | VOLATILE ;
declarator
    : pointer direct_declarator
    | direct_declarator
    ;
direct_declarator
    : IDENTIFIER
    | '(' declarator ')'
    | direct_declarator '[' constant_expression ']'
    | direct_declarator '[' ']'
    | direct_declarator '(' parameter_type_list ')'
    | direct_declarator '(' identifier_list ')'
    | direct_declarator '(' ')'
    ;
pointer
    : '*'
    | '*' type_qualifier_list
    | '*' pointer
    | '*' type_qualifier_list pointer
    ;
type_qualifier_list
    : type_qualifier
    | type_qualifier_list type_qualifier
    ;
parameter_type_list
    : parameter_list
    | parameter_list ',' ELLIPSIS
    ;
parameter_list
    : parameter_declaration
    | parameter_list ',' parameter_declaration
    ;
parameter_declaration
    : declaration_specifiers declarator
    | declaration_specifiers abstract_declarator
    | declaration_specifiers
    ;
identifier_list
    : IDENTIFIER
    | identifier_list ',' IDENTIFIER
    ;
type_name
    : specifier_qualifier_list
    | specifier_qualifier_list abstract_declarator
    ;
abstract_declarator
    : pointer
    | direct_abstract_declarator
    | pointer direct_abstract_declarator
    ;
direct_abstract_declarator
    : '(' abstract_declarator ')'
    | '[' ']'
    | '[' constant_expression ']'
    | direct_abstract_declarator '[' ']'
    | direct_abstract_declarator '[' constant_expression ']'
    | '(' ')'
    | '(' parameter_type_list ')'
    | direct_abstract_declarator '(' ')'
    | direct_abstract_declarator '(' parameter_type_list ')'
    ;
initializer
    : assignment_expression
    | '{' initializer_list '}'
    | '{' initializer_list ',' '}'
    ;
initializer_list
    : initializer
    | initializer_list ',' initializer
    ;

statement
    : labeled_statement
    | compound_statement
    | expression_statement
    | selection_statement
    | iteration_statement
    | jump_statement
    ;
labeled_statement
    : IDENTIFIER ':' statement
    | CASE constant_expression ':' statement
    | DEFAULT ':' statement
    ;
compound_statement
    : '{' '}'
    | '{' statement_list '}'
    | '{' declaration_list '}'
    | '{' declaration_list statement_list '}'
    ;
declaration_list
    : declaration
    | declaration_list declaration
    ;
statement_list
    : statement
    | statement_list statement
    ;
expression_statement
    : ';'
    | expression ';'
    ;
selection_statement
    : IF '(' expression ')' statement
    | IF '(' expression ')' statement ELSE statement
    | SWITCH '(' expression ')' statement
    ;
iteration_statement
    : WHILE '(' expression ')' statement
    | DO statement WHILE '(' expression ')' ';'
    | FOR '(' expression_statement expression_statement ')' statement
    | FOR '(' expression_statement expression_statement expression ')' statement
    ;
jump_statement
    : GOTO IDENTIFIER ';'
    | CONTINUE ';'
    | BREAK ';'
    | RETURN ';'
    | RETURN expression ';'
    ;

translation_unit
    : external_declaration
    | translation_unit external_declaration
    ;
external_declaration
    : function_definition
    | declaration
    ;
function_definition
    : declaration_specifiers declarator declaration_list compound_statement
    | declaration_specifiers declarator compound_statement
    | declarator declaration_list compound_statement
    | declarator compound_statement
    ;
"""

grammar = grammar_from_bnf(C_BNF, "translation_unit")


@functools.cache
def parsing_table() -> ParsingTable:
    """
    Returns the LR1 parsing table of the grammar, generated once per test run.
    """
    return LR1Generator(grammar).generate()


_KEYWORDS = {
    word: word.upper()
    for word in [
        "auto", "break", "case", "char", "const", "continue", "default", "do",
        "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
        "long", "register", "return", "short", "signed", "sizeof", "static",
        "struct", "switch", "typedef", "union", "unsigned", "void", "volatile",
        "while",
    ]
}  # fmt: skip

_TAG_KEYWORDS = {"STRUCT", "UNION", "ENUM"}

_PUNCTUATORS = {
    "...": "ELLIPSIS",
    ">>=": "RIGHT_ASSIGN",
    "<<=": "LEFT_ASSIGN",
    "+=": "ADD_ASSIGN",
    "-=": "SUB_ASSIGN",
    "*=": "MUL_ASSIGN",
    "/=": "DIV_ASSIGN",
    "%=": "MOD_ASSIGN",
    "&=": "AND_ASSIGN",
    "^=": "XOR_ASSIGN",
    "|=": "OR_ASSIGN",
    ">>": "RIGHT_OP",
    "<<": "LEFT_OP",
    "++": "INC_OP",
    "--": "DEC_OP",
    "->": "PTR_OP",
    "&&": "AND_OP",
    "||": "OR_OP",
    "<=": "LE_OP",
    ">=": "GE_OP",
    "==": "EQ_OP",
    "!=": "NE_OP",
}
_PUNCTUATORS |= {char: char for char in ";{},:=()[].&!~-+*/%<>^|?"}

_TOKEN_RE = re.compile(
    r"""
      (?P<skip> \s+ | /\*.*?\*/ | //[^\n]* | ^[ \t]*\#[^\n]* )
    | (?P<constant>
          (?: \d+\.\d* | \.\d+ ) (?: [eE][+-]?\d+ )? [fFlL]?
        | \d+ [eE][+-]?\d+ [fFlL]?
        | 0[xX][0-9a-fA-F]+ [uUlL]*
        | \d+ [uUlL]*
        | L?'(?: \\. | [^\\'\n] )+'
      )
    | (?P<string> L?"(?: \\. | [^\\"\n] )*" )
    | (?P<identifier> [A-Za-z_]\w* )
    | (?P<punctuator> """
    + "|".join(re.escape(p) for p in sorted(_PUNCTUATORS, key=len, reverse=True))
    + ")",
    re.VERBOSE | re.MULTILINE | re.DOTALL,
)


def tokenize(source: str, typedef_names: Collection[str] = ()) -> Iterator[Token]:
    """
    Yields the tokens of the C source, each with its lexeme as its value, and
    then the EOF token. Preprocessor lines and comments are skipped, and names in
    `typedef_names` are type names after their declaration.

    Raises `ValueError` on a character that starts no token.
    """
    declared: set[str] = set()
    previous = None
    position = 0
    while position < len(source):
        match = _TOKEN_RE.match(source, position)
        if match is None:
            raise ValueError(f"Unexpected {source[position]!r} at {position}.")

        position = match.end()
        kind, lexeme = match.lastgroup, match.group()
        if kind == "skip":
            continue

        if kind == "constant":
            symbol = "CONSTANT"
        elif kind == "string":
            symbol = "STRING_LITERAL"
        elif kind == "identifier":
            if lexeme in _KEYWORDS:
                symbol = _KEYWORDS[lexeme]
            elif previous in _TAG_KEYWORDS:
                symbol = "IDENTIFIER"
            elif lexeme in declared:
                symbol = "TYPE_NAME"
            else:
                symbol = "IDENTIFIER"
                if lexeme in typedef_names:
                    declared.add(lexeme)
        else:
            symbol = _PUNCTUATORS[lexeme]

        previous = symbol
        yield Token(symbol, True, lexeme)

    yield Token.eof()


def source_parser() -> LR1Parser:
    """
    Returns a parser whose callbacks rebuild the source from the tokens, with
    every expression of more than one symbol in parentheses and the parentheses
    of the source dropped, so the result shows how the parser grouped it.
    Rules can be given other callbacks with `execute_on`.
    """
    parser = LR1Parser(parsing_table())
    for rule in grammar.rules:
        parser.execute_on(rule)(_source_callback(rule))

    return parser


def _source_callback(rule: Rule) -> Callable[..., str]:
    lhs = rule.lhs.symbol
    if lhs == "primary_expression" and rule.rhs_len == 3:
        return lambda _left, expression, _right: expression.value

    parenthesize = lhs.endswith("expression") and rule.rhs_len > 1

    def callback(*tokens: Token) -> str:
        text = " ".join(token.value for token in tokens if token.value)
        return f"({text})" if parenthesize else text

    return callback
