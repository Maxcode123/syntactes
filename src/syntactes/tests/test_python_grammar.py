import ast

from unittest_extensions import TestCase, args

from syntactes.parser import UnexpectedTokenError
from syntactes.tests import python_grammar

MODULE = '''\
"""
An inventory of products, with a multi-line docstring.
"""

import collections.abc as abc, sys
from . import config
from ..storage import (load, save as store,)
from decimal import *

DEFAULT_TAX: float = 0.2
_registry = {}


def register(name, *, replace=False):
    def decorator(cls):
        if name in _registry and not replace:
            raise KeyError(name) if name else ValueError("empty name")
        _registry[name] = cls
        return cls
    return decorator


@register("product")
class Product(abc.Hashable, metaclass=type):
    """A product with a price in cents."""

    count = 0

    def __init__(self, name: str, price: int = 0, /, *tags, stock=1, **extra) -> None:
        self.name, self.price = name, price
        self.tags = {tag.lower() for tag in tags if tag}
        self.stock = stock
        self.extra = {**extra, "created": True}
        Product.count += 1

    def __hash__(self):
        return hash((self.name, self.price))

    @property
    def gross(self):
        return round(self.price * (1 + DEFAULT_TAX))

    def __repr__(self):
        return "Product(%r, %d)" % (self.name, self.price)


class Inventory:
    def __init__(self, products=()):
        self._items = collections.OrderedDict((p.name, p) for p in products)

    def __getitem__(self, name):
        try:
            return self._items[name]
        except KeyError as error:
            raise LookupError(name) from error
        finally:
            pass

    def cheapest(self, n=1):
        return sorted(self._items.values(), key=lambda p: (p.price, p.name))[:n]

    def restock(self, **amounts):
        for name, amount in amounts.items():
            if amount <= 0:
                continue
            elif name not in self._items:
                break
            else:
                self[name].stock += amount
        else:
            return True
        return False

    def report(self, out=sys.stdout):
        total = 0
        for i, (name, product) in enumerate(self._items.items(), start=1):
            total += product.gross * product.stock
            print(i, name, product.gross, sep="\\t", file=out)
        assert total >= 0, "negative total"
        return total
'''

ALGORITHMS = """\
from functools import reduce, wraps


def memoize(function):
    cache = {}

    @wraps(function)
    def wrapper(*args):
        if args not in cache:
            cache[args] = function(*args)
        return cache[args]

    return wrapper


@memoize
def fibonacci(n):
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)


def quicksort(items):
    if len(items) <= 1:
        return items
    pivot, *rest = items
    return (
        quicksort([x for x in rest if x < pivot])
        + [pivot]
        + quicksort([x for x in rest if x >= pivot])
    )


def counter():
    count = 0

    def increment(step=1):
        nonlocal count
        count += step
        return count

    return increment


def primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = [False] * len(sieve[i * i :: i])
    yield from (i for i, is_prime in enumerate(sieve) if is_prime)


def chunks(data, size):
    while chunk := data[:size]:
        yield chunk
        data = data[size:]


def flatten(matrix):
    return [cell for row in matrix for cell in row if cell is not None]


def bits(n):
    return n & 0xFF | n >> 8 ^ ~n << 2, -n % 3, n // 2 ** -1, 1_000.5e-3j


matrix = [[1, 2], [3, None]]
grid = {(x, y): x * y for x in range(3) for y in range(3) if x != y}
total = reduce(lambda a, b: a + b, flatten(matrix), 0)
first, (second, *others) = 1, (2, 3, 4)
del matrix[0][:], grid[0, 1]
with open("in") as src, open("out", "w") as dst:
    dst.write(src.read().strip().upper()[::-1])
print(not total == 6 and total in {6, 7} or b'bytes' rb'raw', end='')
"""

ASYNC = """\
import asyncio


async def fetch(session, url, *, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                return await response.json()
        except asyncio.TimeoutError:
            await asyncio.sleep(2 ** attempt)
    return None


async def ticker(delay, to):
    for i in range(to):
        yield i
        await asyncio.sleep(delay)


async def main(urls):
    results = await asyncio.gather(*(fetch(None, url) for url in urls))
    squares = [i ** 2 async for i in ticker(0.1, 10) if i % 2]
    async for value in ticker(0, 3):
        print(value, *squares, sep=", ")
    return {url: result for url, result in zip(urls, results)}


asyncio.run(main(["a", "b"]))
"""

SMALL_STATEMENTS = """\
x = y = z = 0; a += 1; b: int; c: list = []
pass; del x
global q
if x: pass
elif y: pass
else: return_value = (yield)
while False: break
class Empty: ...
def nothing(): return
lambda: (yield)
raise
"""


class TestPythonParsingTable(TestCase):
    def subject(self):
        return python_grammar.parsing_table().conflicts()

    def test_no_conflicts(self):
        self.assertResult([])


class TestPythonExpressions(TestCase):
    def subject(self, expression):
        source = python_grammar.source_parser().parse(
            python_grammar.tokenize(expression + "\n")
        )
        return str(source).strip()

    @args("a + b * c")
    def test_term_over_arith(self):
        self.assertResult("(a + (b * c))")

    @args("a - b - c")
    def test_arith_left_associative(self):
        self.assertResult("((a - b) - c)")

    @args("a @ b // c % d")
    def test_term_left_associative(self):
        self.assertResult("(((a @ b) // c) % d)")

    @args("2 ** 3 ** 2")
    def test_power_right_associative(self):
        self.assertResult("(2 ** (3 ** 2))")

    @args("-2 ** 2")
    def test_power_over_unary_minus(self):
        self.assertResult("(- (2 ** 2))")

    @args("a ** -b")
    def test_unary_minus_in_exponent(self):
        self.assertResult("(a ** (- b))")

    @args("~a + b")
    def test_unary_over_arith(self):
        self.assertResult("((~ a) + b)")

    @args("a | b ^ c & d << e + f * g")
    def test_bitwise_precedence(self):
        self.assertResult("(a | (b ^ (c & (d << (e + (f * g))))))")

    @args("not a and b or c")
    def test_boolean_precedence(self):
        self.assertResult("(((not a) and b) or c)")

    @args("a or b and not c")
    def test_boolean_precedence_right(self):
        self.assertResult("(a or (b and (not c)))")

    @args("not a in b")
    def test_comparison_over_not(self):
        self.assertResult("(not a in b)")

    @args("a + b < c * d")
    def test_arith_over_comparison(self):
        self.assertResult("(a + b) < (c * d)")

    @args("a < b <= c is not d not in e")
    def test_chained_comparison(self):
        self.assertResult("a < b <= c is not d not in e")

    @args("a if b else c if d else e")
    def test_conditional_right_associative(self):
        self.assertResult("(a if b else (c if d else e))")

    @args("lambda x, *y: x + 1 if x else y")
    def test_lambda_body(self):
        self.assertResult("(lambda x , * y : ((x + 1) if x else y))")

    @args("a.b(c)[d]")
    def test_trailers_left_to_right(self):
        self.assertResult("(((a . b) ( c )) [ d ])")

    @args("await a.b ** 2")
    def test_await_over_power(self):
        self.assertResult("((await (a . b)) ** 2)")

    @args("(x := a + 1)")
    def test_assignment_expression(self):
        self.assertResult("( (x := (a + 1)) )")


class TestPythonMatchesAst(TestCase):
    """
    The parser's source, with every expression in parentheses, parses to the
    same AST as the original exactly when the parser grouped it as Python does.
    """

    def subject(self, source):
        return python_grammar.source_parser().parse(python_grammar.tokenize(source))

    def assert_same_ast(self, source):
        self.assertEqual(
            ast.dump(ast.parse(self.result())), ast.dump(ast.parse(source))
        )

    @args(MODULE)
    def test_module(self):
        self.assert_same_ast(MODULE)

    @args(ALGORITHMS)
    def test_algorithms(self):
        self.assert_same_ast(ALGORITHMS)

    @args(ASYNC)
    def test_async(self):
        self.assert_same_ast(ASYNC)

    @args(SMALL_STATEMENTS)
    def test_small_statements(self):
        self.assert_same_ast(SMALL_STATEMENTS)


class TestPythonRejects(TestCase):
    """
    Each source is a syntax error for CPython too.
    """

    def subject(self, source):
        with self.assertRaises(SyntaxError):
            ast.parse(source)

        try:
            python_grammar.source_parser().parse(python_grammar.tokenize(source))
        except UnexpectedTokenError as error:
            return str(error.received_token)

    @args("def f(:\n    pass\n")
    def test_missing_parameter(self):
        self.assertResult(":")

    @args("x = = 1\n")
    def test_missing_value(self):
        self.assertResult("=")

    @args("if x\n    pass\n")
    def test_missing_colon(self):
        self.assertResult("NEWLINE")

    @args("if x:\npass\n")
    def test_missing_indent(self):
        self.assertResult("pass")

    @args("a +\n")
    def test_missing_operand(self):
        self.assertResult("NEWLINE")

    @args("1 + *a\n")
    def test_starred_operand(self):
        self.assertResult("*")

    @args("a if b\n")
    def test_conditional_without_else(self):
        self.assertResult("NEWLINE")

    @args("try:\n    pass\nelse:\n    pass\n")
    def test_try_without_handler(self):
        self.assertResult("else")

    @args("for x in :\n    pass\n")
    def test_for_without_iterable(self):
        self.assertResult(":")

    @args("from x import\n")
    def test_import_without_names(self):
        self.assertResult("NEWLINE")

    @args("f(**)\n")
    def test_double_star_without_operand(self):
        self.assertResult(")")

    @args("class A(:\n    pass\n")
    def test_class_without_bases(self):
        self.assertResult(":")
