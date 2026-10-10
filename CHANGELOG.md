# Changelog

## 0.8.0 - Unreleased

### Breaking changes

- `Rule` no longer takes a primitive: it's `Rule(number, lhs, *rhs)` again,
  and `Rule.primitive` is removed. Primitives are in `Grammar.primitives`, and
  `str(rule)` no longer prints them. Calls written for 0.7, like
  `Rule(0, None, S, E, EOF)`, don't raise, but read `None` as the left-hand
  side.

### Added

- The `bool` primitive (`Boolean`), and binary operation primitives that take
  two operands: `add`, `sub`, `mul`, `div`, `pow` (`Addition`, `Subtraction`,
  `Multiplication`, `Division`, `Exponentiation`) and `lt`, `le`, `gt`, `ge`,
  `eq`, `ne` (`LowerThanComparison`, `LowerEqualThanComparison`,
  `GreaterThanComparison`, `GreaterEqualThanComparison`, `EqualityComparison`,
  `InequalityComparison`).

- `syntactes.primitive.primitives()` returns every primitive.

- `Grammar.primitives`, a read-only mapping from rules to their primitive.
  `Grammar` takes it as the keyword-only argument `primitives`, and raises
  `GrammarError` for a rule that's not in the grammar or a value that isn't a
  primitive. `Grammar.from_text` fills it from `int % expr -> NUMBER` lines.

- Binary operations can name their operands by 1-based position, as in
  `add(1,3) % expr -> expr PLUS expr`, and default to the first and last
  symbols. The positions are in `Grammar.operands`, which `Grammar` also takes
  as the keyword-only argument `operands`.

- The error for an unknown primitive in `Grammar.from_text` lists every valid
  name.

### Changed

- Removes the `syntactes.ast` module. It shipped in 0.7.0 and 0.7.1, but was
  never exported or documented.

## 0.7.1 - 2026-10-08

### Added

- `syntactes.parser` exports the `Parser` base class of `LR0Parser`,
  `SLRParser` and `LR1Parser`.

## 0.7.0 - 2026-10-08

### Breaking changes

- `Rule` takes a primitive (or `None`) as its second argument:
  `Rule(number, primitive, lhs, *rhs)`. Old calls like `Rule(0, S, E, EOF)`
  don't raise, but read `S` as the primitive and `E` as the left-hand side.

### Added

- Rules can have a primitive type. In `Grammar.from_text` it's written before
  the left-hand side, as in `int % expr -> NUMBER`, with one of `int`, `float`,
  `str` or `None`. It's stored as `Rule.primitive`, one of the new
  `syntactes.primitive` classes `Integer`, `Float`, `String` and `NoneType`,
  and printed by `str(rule)`.

- A documentation site at https://maximosnikiforakis.gr/syntactes/, with guide
  pages for grammars, parsing tables and parsing, and an API reference.

## 0.6.0 - 2026-10-07

### Added

- `Grammar.from_text` builds a grammar from text, one `lhs -> symbols` rule per
  line with `#` comments. Names on a left-hand side are non-terminals, and
  every other symbol is a terminal. The starting rule `<start> -> lhs $` is
  added as rule 0.
- `GrammarError.problems` holds every error as `(line, message)` pairs.
  `from_text` reports all of them at once.
- `GrammarWarning`, emitted by `from_text` for each non-terminal that can't be
  reached from the start symbol or can't derive a string of terminals.
- `Grammar.terminals()`.

## 0.5.0 - 2026-10-07

### Breaking changes

- Requires Python 3.13.
- Callbacks are registered per parser with `@parser.execute_on(rule)`, which
  raises `ValueError` for a rule outside the parser's grammar. The module-level
  `execute_on` and `ExecutablesRegistry` are removed.
- `Grammar` validates the grammar and raises `GrammarError` (a `ValueError`)
  if it's malformed.

### Added

- A callback's return value becomes the `value` of the token pushed for the
  left-hand side, and `parse()` returns the starting rule callback's value.
- Parsing tables expose their `grammar`.

### Changed

- Table generation is deterministic: states are numbered breadth-first, and
  the output doesn't depend on `PYTHONHASHSEED`.
- Conflicts are resolved the way yacc resolves them: shift wins over reduce,
  and between reduces the rule with the lowest number wins.
- `UnexpectedTokenError.expected_tokens` lists only terminals, sorted.
- Printed tables number rules by their rule number, pad their cells and leave
  out the `ε` column.
- Large grammars generate much faster.

### Fixed

- Reduce callbacks received the right-hand side tokens in reverse order.
- Parse state was kept on the parser between parses, and an empty stream
  raised `UnboundLocalError`.
- Empty rules (`Rule(n, A)` or `Rule(n, A, Token.null())`) can now be reduced,
  and their callbacks are called with no arguments.
- Nullable symbols in FIRST and FOLLOW sets, LR0 closures, and LR1 closure
  lookaheads, which made some tables wrong.

## 0.4.0 - 2024-12-19

### Added

- `LR1Generator`, `LR1ParsingTable` and `LR1Parser`.
- `Rule.has_null_rhs()`.

### Changed

- FIRST sets take nullable symbols into account.

## 0.3.1 - 2024-11-05

### Fixed

- The distribution includes the `syntactes.parser` and
  `syntactes.parsing_table` subpackages.

## 0.3.0 - 2024-11-05

### Added

- `conflicts()` on parsing tables, which lists the cells with more than one
  action as `Conflict`s.

## 0.2.0 - 2024-11-05

### Added

- `LR0Parser` and `SLRParser`, with `from_grammar()`, and callbacks
  registered with `execute_on`.
- `ParserError`, `UnexpectedTokenError` and `NotAcceptedError`.
- `Token.value`.

## 0.1.2 - 2024-11-02

### Added

- `SLRParsingTable`, whose printout is headed "SLR PARSING TABLE".

## 0.1.1 - 2024-11-01

- First releases (0.1.0 and 0.1.1), with the LR0 and SLR parsing table
  generators.
