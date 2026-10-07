# syntactes

A simple Python parser generator. You give it a grammar (tokens and rules), and
it builds LR0, SLR or LR1 parsing tables and parsers that run user callbacks on
each reduction. It's a library published on PyPI. Docs are at
https://maximosnikiforakis.gr/syntactes/.

## Commands

Use uv for everything. Dev tools (unittest-extensions, ruff, ty, and mkdocs for
the docs) are in the `dev` dependency group, locked in `uv.lock`. Bare `python`
doesn't work here, because there's no `.python-version` for pyenv. Always go
through `uv run python …`.

```sh
make test          # whole unit suite (unittest discover)
make lint          # ruff check
make type-check    # ty
make format        # ruff format (src and examples)
uv run python -m unittest syntactes.tests.test_parser   # one module
uv run python examples/parser.py                        # run an example
uv run mkdocs build --strict -d <scratch dir>           # check the docs
make start-doc-server                                   # serve the docs locally
```

Before every commit, run `make test`, `make lint` and `make type-check`, and
make sure `uv run ruff format --check src examples` is clean. CI
(`.github/workflows/test-package.yml`) runs the same four checks on Python
3.13, for pushes to `main` and `tester/*` and for PRs.

Tooling notes:

- ty and ruff target Python 3.13, which they take from `requires-python`.
- The `__init__.py` files use `# isort: skip_file`. Their import order resolves
  the circular imports between package modules, so don't sort them.
- Table generation is deterministic: states are numbered breadth-first and
  output doesn't depend on `PYTHONHASHSEED`. `test_determinism.py` checks
  this across seeds, and CI runs the suite under several.

## Architecture

All code lives in `src/syntactes/`:

- `token.py`: `Token` (a symbol, `is_terminal`, and an optional `value`), with
  `Token.eof()` (`$`) and `Token.null()` (`ε`). Equality and hashing ignore
  `value`.
- `rule.py`: `Rule(number, lhs, *rhs)`.
- `grammar.py`: `Grammar(starting_rule, rules, tokens)`, `Grammar.from_text`,
  `GrammarError` (with `problems`, a list of `(line, message)`) and
  `GrammarWarning`.
- `_text.py`: parses the text format for `Grammar.from_text`, collecting every
  error, and computes its warnings (unreachable and unproductive non-terminals).
- `_item.py`, `_state.py`, `_action.py`: private LR0/LR1 items, states and
  shift/reduce/accept actions. `LR1Item` subclasses `LR0Item` and `LR1State`
  subclasses `LR0State`, so code typed with the LR0 classes accepts both. `State`
  is a protocol.
- `generator.py`: `LR0Generator`, `SLRGenerator` and `LR1Generator`. They compute
  FIRST/FOLLOW sets (nullable symbols included), closures and gotos, and their
  `generate()` returns a parsing table. `Generator` is generic over its item and
  state types (`Generator[LR1Item, LR1State]`).
- `parsing_table/`: `Entry`, `Conflict` / `ConflictType`, the `ParsingTable`
  protocol, and the `LR0ParsingTable`, `SLRParsingTable` and `LR1ParsingTable`
  classes. These have `from_entries(entries, grammar)`, `pretty_str()` and
  `conflicts()`. The subclasses only change the header.
- `parser/`:
  - `parser.py`: `LR0Parser`, `SLRParser` and `LR1Parser`, built from a table or
    with `from_grammar()`. `@parser.execute_on(rule)` registers a callback on
    that parser. On each reduction it's called with one token per RHS symbol,
    and its return value becomes the `value` of the pushed LHS token.
    `parse(stream)` consumes tokens and returns the starting rule callback's
    value.
  - `exception.py`: `ParserError` and its subclasses.
- `tests/`: `data.py` holds the shared test grammars, rules, states and parsing
  tables. `test_generator.py` and `test_parser.py` use them.
  `c_grammar.py` (ANSI C89) and `python_grammar.py` (Python 3.8) hold real
  language grammars, written in the yacc-like BNF that `_bnf.py` loads, with a
  lexer and a parser whose callbacks rebuild the source with every expression
  in parentheses. Their LR1 tables take a few seconds to generate and are
  cached per test run.

`examples/` holds runnable scripts. They're not part of the package.

The docs site (`mkdocs.yml`, `docs/`) is MkDocs Material with mkdocstrings,
laid out like the lectes docs (`../lectes`). Its guide pages are
`grammars.md`, `parsing-tables.md` and `parsing.md`. It shares lectes's arcade
look, with its own green phosphor palette: `docs/stylesheets/arcade.css` maps
Material's dark (`slate`) palette onto the `--sx-*` colours. The fonts in
`docs/assets/fonts/` are copied from lectes.

## Rules

- **No runtime dependencies** (`dependencies = []`). Use the stdlib only, and
  so no `typing_extensions` either. Adding a runtime dependency needs explicit
  approval. Dev-only tools go in the `dev` dependency group
  (`uv add --dev …`).
- **Python 3.13+** (`requires-python = ">=3.13"`). Modern syntax is fine, and
  ruff enforces it. Use PEP 695 generics (`class Generator[ItemT: LR0Item]`),
  `type` aliases, and `typing.Self`.
- **The public API** is everything exported from `syntactes/__init__.py`,
  `syntactes/parser/__init__.py` and `syntactes/parsing_table/__init__.py`, plus
  the behaviour the README shows. Point out any breaking change and get
  agreement before making it.
- New public names go in the relevant `__init__.py`. Modules prefixed with `_`
  are private.

## Workflow

- **Test first, always.** For every behaviour change or bug fix:
  1. Write the tests.
  2. Run them and watch them fail.
  3. Implement until they pass.

  Tests and implementation go in the same commit.
- **Tests** use `unittest` with `unittest-extensions`. A test class defines
  `subject(...)`, test methods are decorated with `@args(...)`, and they call
  `self.result()`, `self.assertResult(...)` or
  `self.assertResultRaises(...)`. Shared setup and assert helpers go on a base
  `TestCase`. New grammars, states and tables go in `tests/data.py`, except
  full language grammars, which get a module of their own.
- **Git:**
  - Always work on a branch, never directly on `main`.
  - Make small atomic commits, each one passing the checks.
  - Write commit subjects in the present tense, third person, e.g. "Adds …",
    "Defines …", "Fixes …", "Increments version to X.Y.Z". Add a body
    explaining *why* when it isn't obvious.
  - Don't merge into `main`, push, tag, publish or deploy docs unless asked.
    When asked to merge, use `git merge --no-ff <branch>` (message:
    `Merge branch '<branch>'`).
- **Docs go with every user-facing change, on the same branch:**
  - Update the relevant `docs/*.md` page, and `README.md` and `examples/` if
    needed. Run every code sample you add, and paste its real output. Don't
    print anything whose order changes between runs, like a state's items.
  - Add a bullet under `## X.Y.Z - Unreleased` in `CHANGELOG.md`, in the
    `Breaking changes` / `Added` / `Changed` / `Fixed` sections.
  - New pages go in the `mkdocs.yml` nav. API pages are `::: module` stubs
    rendered by mkdocstrings, which leaves out objects without a docstring,
    so give new public classes and methods one.
- **Code style:**
  - Formatting is ruff's (line length 88).
  - Type hints everywhere, and ty must pass. Prefer real narrowing (e.g.
    `if x is None`) over `cast`. Use `cast` only where an invariant can't be
    expressed, like an action's `actionable` being a state for shifts and a
    rule for reduces.
  - Prefix private helpers and modules with `_`.
  - Docstrings are triple-quoted, with the text starting on the next line.
- `.envrc` holds secrets and is git-ignored. Never print it or commit it.

## Release (only when asked)

1. On the branch, set `version` in `pyproject.toml`, run `uv lock`, change
   `## X.Y.Z - Unreleased` in `CHANGELOG.md` to today's date, and commit as
   "Increments version to X.Y.Z".
2. Merge into `main` with `--no-ff`, run `make test`, then
   `git push origin main`.
3. Run `git tag vX.Y.Z` (with a `v` prefix, like the earlier tags), then
   `git push origin vX.Y.Z`.
4. Run `make clean build-package` (`uv build`). Check that `dist/` holds only
   X.Y.Z, and that the wheel has what you expect (e.g. `unzip -l dist/*.whl`).
   It should hold all subpackages and no `tests`.
5. Run `make upload-package` (`uv publish`). It reads `UV_PUBLISH_TOKEN` from
   `.envrc` (via direnv). Never print it.
6. Run `make deploy-documentation` (`mkdocs gh-deploy`). GitHub Pages takes a
   few minutes to rebuild. Check progress with
   `gh api repos/Maxcode123/syntactes/pages/builds/latest`.
7. Verify from outside the repo, with `PYTHONPATH` unset:
   `uvx --refresh --from syntactes==X.Y.Z python -c "import syntactes"`. Then
   run an example against it, and check the changed docs pages on the live
   site.

Pitfalls:

- Never build unreleased code into `dist/` under an already-released version
  number. To try a local build, use `uv build -o <scratch dir>`.
- Because of `PYTHONPATH`, importing `syntactes` from the repo always loads
  `src/`. To test the installed package, run from outside the repo with
  `PYTHONPATH` unset.
