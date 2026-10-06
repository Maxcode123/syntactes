from unittest_extensions import TestCase, args

from syntactes.parser import UnexpectedTokenError
from syntactes.parsing_table import ConflictType
from syntactes.tests import c_grammar
from syntactes.tests._bnf import find_rule

PROGRAM = r"""
#include <stdio.h>
#include <stdlib.h>

typedef struct node {
    int value;
    struct node *next;
} node_t;

typedef int (*compare_fn)(const void *, const void *);

enum color { RED, GREEN = 2, BLUE };

static const char *names[] = { "red", "green", "blue", };
static unsigned long counter = 0x10UL;
extern int errno;

/* Pushes a value onto the front of the list. */
node_t *push(node_t *head, int value)
{
    node_t *node = (node_t *) malloc(sizeof(node_t));

    if (node == NULL)
        return head;
    node->value = value;
    node->next = head;
    counter += 1;
    return node;
}

int length(head)
    node_t *head;
{
    int n = 0;

    for (; head != 0; head = head->next)
        n++;
    return n;
}

static int compare(const void *a, const void *b)
{
    int x = *(const int *) a, y = *(const int *) b;

    return x < y ? -1 : x > y;
}

void describe(enum color c, char buffer[], int size)
{
    switch (c) {
    case RED:
        sprintf(buffer, "%s!", names[c]);
        break;
    case GREEN:
    case BLUE:
        if (size > 10 && buffer != 0)
            sprintf(buffer, "%s", names[c]);
        else
            buffer[0] = '\0';
        break;
    default:
        goto done;
    }
done:
    return;
}

int main(int argc, char **argv)
{
    int values[5] = { 3, 1, 4, 1, 5 };
    compare_fn cmp = compare;
    node_t *list = 0;
    double ratio = 1.5e-3;
    int i = 0;

    do {
        list = push(list, values[i] << 1 | 1);
    } while (++i < (int) (sizeof values / sizeof values[0]));

    qsort(values, 5, sizeof(int), cmp);
    while (list) {
        node_t *next = list->next;
        free(list);
        list = next;
        if (!list)
            continue;
    }
    ratio *= argc > 1 ? atof(argv[1]) : 2.0;
    printf("%d %f\n", length(list), ratio);
    return 0;
}
"""


class TestCParsingTable(TestCase):
    def subject(self):
        return c_grammar.parsing_table().conflicts()

    # The only conflict of the ANSI C grammar is the dangling else.
    def test_only_dangling_else_conflicts(self):
        self.assertSetEqual(
            {(c.token.symbol, c.conflict_type) for c in self.result()},
            {("ELSE", ConflictType.SHIFT_REDUCE)},
        )


class TestCExpressions(TestCase):
    def subject(self, expression):
        parser = c_grammar.source_parser()
        expressions = []
        rule = find_rule(c_grammar.grammar, "expression_statement", "expression", "';'")
        parser.execute_on(rule)(lambda e, _semicolon: expressions.append(e.value))
        parser.parse(c_grammar.tokenize(f"void f(void) {{ {expression}; }}"))
        return expressions

    def assert_grouped(self, grouped):
        self.assertResult([grouped])

    @args("a + b * c")
    def test_multiplicative_over_additive(self):
        self.assert_grouped("(a + (b * c))")

    @args("a * (b + c)")
    def test_parentheses(self):
        self.assert_grouped("(a * (b + c))")

    @args("a - b - c")
    def test_additive_left_associative(self):
        self.assert_grouped("((a - b) - c)")

    @args("a % b / c")
    def test_multiplicative_left_associative(self):
        self.assert_grouped("((a % b) / c)")

    @args("a << b + c")
    def test_additive_over_shift(self):
        self.assert_grouped("(a << (b + c))")

    @args("a < b == c > d")
    def test_relational_over_equality(self):
        self.assert_grouped("((a < b) == (c > d))")

    @args("a & b == c")
    def test_equality_over_bitwise_and(self):
        self.assert_grouped("(a & (b == c))")

    @args("a & b ^ c | d")
    def test_bitwise_precedence(self):
        self.assert_grouped("(((a & b) ^ c) | d)")

    @args("a || b && c")
    def test_logical_and_over_logical_or(self):
        self.assert_grouped("(a || (b && c))")

    @args("a ? b : c ? d : e")
    def test_conditional_right_associative(self):
        self.assert_grouped("(a ? b : (c ? d : e))")

    @args("a = b = c")
    def test_assignment_right_associative(self):
        self.assert_grouped("(a = (b = c))")

    @args("a += b -= c")
    def test_compound_assignment_right_associative(self):
        self.assert_grouped("(a += (b -= c))")

    @args("a = b ? c : d")
    def test_conditional_over_assignment(self):
        self.assert_grouped("(a = (b ? c : d))")

    @args("a, b = c")
    def test_assignment_over_comma(self):
        self.assert_grouped("(a , (b = c))")

    @args("*p++")
    def test_postfix_over_unary(self):
        self.assert_grouped("(* (p ++))")

    @args("++*p")
    def test_unary_right_to_left(self):
        self.assert_grouped("(++ (* p))")

    @args("-a * b")
    def test_unary_over_multiplicative(self):
        self.assert_grouped("((- a) * b)")

    @args("!a && ~b")
    def test_unary_operators(self):
        self.assert_grouped("((! a) && (~ b))")

    @args("(int) a + b")
    def test_cast_over_additive(self):
        self.assert_grouped("((( int ) a) + b)")

    @args("(unsigned char *) p")
    def test_cast_to_pointer(self):
        self.assert_grouped("(( unsigned char * ) p)")

    @args("sizeof a + b")
    def test_sizeof_expression(self):
        self.assert_grouped("((sizeof a) + b)")

    @args("sizeof (int) * 2")
    def test_sizeof_type(self):
        self.assert_grouped("((sizeof ( int )) * 2)")

    @args("f(a, b)[i].x->y")
    def test_postfix_left_to_right(self):
        self.assert_grouped("((((f ( a , b )) [ i ]) . x) -> y)")

    @args("f(a = 1, (b, c))")
    def test_arguments(self):
        self.assert_grouped("(f ( (a = 1) , (b , c) ))")

    @args("x = 'c' + \"s\"[0] + 0x1F + 1.5e3")
    def test_constants(self):
        self.assert_grouped("(x = ((('c' + (\"s\" [ 0 ])) + 0x1F) + 1.5e3))")


class TestCStatements(TestCase):
    def subject(self, statements):
        parser = c_grammar.source_parser()
        for rhs, template in [
            (["IF", "'('", "expression", "')'", "statement"], "[if {} then {}]"),
            (
                ["IF", "'('", "expression", "')'", "statement", "ELSE", "statement"],
                "[if {} then {} else {}]",
            ),
        ]:
            rule = find_rule(c_grammar.grammar, "selection_statement", *rhs)
            parser.execute_on(rule)(
                lambda *tokens, template=template: template.format(
                    *(
                        t.value
                        for t in tokens
                        if t.symbol in ("expression", "statement")
                    )
                )
            )

        return parser.parse(c_grammar.tokenize(f"void f(void) {{ {statements} }}"))

    @args("if (a) if (b) x(); else y();")
    def test_dangling_else_binds_to_nearest_if(self):
        self.assertResult(
            "void f ( void ) { [if a then [if b then (x ( )) ; else (y ( )) ;]] }"
        )

    @args("if (a) { if (b) x(); } else y();")
    def test_braces_bind_else_to_outer_if(self):
        self.assertResult(
            "void f ( void ) { [if a then { [if b then (x ( )) ;] } else (y ( )) ;] }"
        )

    @args("if (a) x(); else if (b) y(); else z();")
    def test_else_if_chain(self):
        self.assertResult(
            "void f ( void ) "
            "{ [if a then (x ( )) ; else [if b then (y ( )) ; else (z ( )) ;]] }"
        )


class TestCAccepts(TestCase):
    def subject(self, source, typedef_names=()):
        return c_grammar.source_parser().parse(
            c_grammar.tokenize(source, typedef_names)
        )

    @args("int *a[10];")
    def test_array_of_pointers(self):
        self.result()

    @args("int (*a)[10];")
    def test_pointer_to_array(self):
        self.result()

    @args("char *(*(*x())[])();")
    def test_nested_declarator(self):
        self.result()

    @args("void (*signal(int sig, void (*func)(int)))(int);")
    def test_function_returning_function_pointer(self):
        self.result()

    @args("int printf(const char *format, ...);")
    def test_variadic_prototype(self):
        self.result()

    @args("struct s { unsigned int flag : 1; int : 0; union { int i; float f; } u; };")
    def test_bit_fields_and_nested_union(self):
        self.result()

    @args("static const volatile int x = 1, y[] = { 1, { 2, 3 }, };")
    def test_qualifiers_and_initializers(self):
        self.result()

    @args("typedef unsigned long size_t; size_t n; size_t f(size_t);", ["size_t"])
    def test_typedef_name(self):
        self.result()

    @args("typedef struct node node; struct node { node *next; };", ["node"])
    def test_typedef_name_same_as_tag(self):
        self.result()

    @args("int f(a, b) int a; char *b; { return a + *b; }")
    def test_old_style_function_definition(self):
        self.result()

    @args("main() { }")
    def test_implicit_int_function_definition(self):
        self.result()

    @args(
        "void f(int n) { int i; for (;;) { } for (i = 0; i < n; i++) ; "
        "while (n--) continue; do n++; while (n < 10); l: goto l; }"
    )
    def test_loops_and_jumps(self):
        self.result()


class TestCProgram(TestCase):
    def subject(self):
        parser = c_grammar.source_parser()
        kinds = []
        for kind in ("function_definition", "declaration"):
            rule = find_rule(c_grammar.grammar, "external_declaration", kind)
            parser.execute_on(rule)(lambda _d, kind=kind: kinds.append(kind))

        parser.parse(c_grammar.tokenize(PROGRAM, {"node_t", "compare_fn"}))
        return kinds

    def test_external_declarations(self):
        self.assertResult(
            ["declaration"] * 6 + ["function_definition"] * 5,
        )


class TestCRejects(TestCase):
    def subject(self, source):
        try:
            c_grammar.source_parser().parse(c_grammar.tokenize(source))
        except UnexpectedTokenError as error:
            return str(error.received_token)

    @args("int main(void) { return 0 }")
    def test_missing_semicolon(self):
        self.assertResult("}")

    @args("int x = ;")
    def test_missing_initializer(self):
        self.assertResult(";")

    @args("void f(void) { if x) return; }")
    def test_missing_parenthesis(self):
        self.assertResult("IDENTIFIER")

    @args("void f(void) { else return; }")
    def test_else_without_if(self):
        self.assertResult("ELSE")

    @args("void f(void) { return 1 + ; }")
    def test_missing_operand(self):
        self.assertResult(";")

    @args("int a b;")
    def test_missing_comma_between_declarators(self):
        self.assertResult("IDENTIFIER")

    @args("struct s { int x; } s")
    def test_unterminated_declaration(self):
        self.assertResult("$")

    @args("void f(void) { int a[; }")
    def test_unterminated_array_declarator(self):
        self.assertResult(";")

    @args("void f(void) { case 1: }")
    def test_label_without_statement(self):
        self.assertResult("}")
