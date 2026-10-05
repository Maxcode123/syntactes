import os
import subprocess
import sys
from pathlib import Path

from unittest_extensions import TestCase, args

_SRC = str(Path(__file__).resolve().parents[2])

_SCRIPT = """
import sys

import syntactes
from syntactes.tests import data

generator_cls = getattr(syntactes, sys.argv[1])
grammar = getattr(data, sys.argv[2])
print(generator_cls(grammar).generate().pretty_str())
"""

_SEEDS = range(5)


def _pretty_str(generator: str, grammar: str, seed: int) -> str:
    env = {**os.environ, "PYTHONHASHSEED": str(seed), "PYTHONPATH": _SRC}
    process = subprocess.run(
        [sys.executable, "-c", _SCRIPT, generator, grammar],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return process.stdout


class TestGenerateIsDeterministic(TestCase):
    def subject(self, generator, grammar):
        return {_pretty_str(generator, grammar, seed) for seed in _SEEDS}

    def assert_same_output(self):
        self.assertEqual(len(self.result()), 1)

    @args("LR0Generator", "grammar_1")
    def test_lr0_grammar_1(self):
        self.assert_same_output()

    @args("SLRGenerator", "grammar_1")
    def test_slr_grammar_1(self):
        self.assert_same_output()

    @args("LR1Generator", "grammar_2")
    def test_lr1_grammar_2(self):
        self.assert_same_output()

    @args("SLRGenerator", "grammar_6")
    def test_slr_grammar_6(self):
        self.assert_same_output()

    @args("LR1Generator", "grammar_6")
    def test_lr1_grammar_6(self):
        self.assert_same_output()

    @args("LR1Generator", "grammar_4")
    def test_lr1_grammar_4(self):
        self.assert_same_output()
