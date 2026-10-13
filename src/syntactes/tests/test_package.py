import importlib

from unittest_extensions import TestCase, args


class TestExports(TestCase):
    def subject(self, module, name):
        return hasattr(importlib.import_module(module), name)

    @args("syntactes.config", "Token")
    def test_config_exports_token(self):
        self.assertResult(True)

    @args("syntactes.config", "Rule")
    def test_config_exports_rule(self):
        self.assertResult(True)

    @args("syntactes.config", "Grammar")
    def test_config_exports_grammar(self):
        self.assertResult(True)

    @args("syntactes.config", "GrammarError")
    def test_config_exports_grammar_error(self):
        self.assertResult(True)

    @args("syntactes.config", "GrammarWarning")
    def test_config_exports_grammar_warning(self):
        self.assertResult(True)

    @args("syntactes.config", "Integer")
    def test_config_exports_value_type(self):
        self.assertResult(True)

    @args("syntactes.config", "Addition")
    def test_config_exports_binary_operation(self):
        self.assertResult(True)

    @args("syntactes.config", "primitives")
    def test_config_exports_primitives(self):
        self.assertResult(True)

    @args("syntactes.generator", "LR0Generator")
    def test_generator_exports_lr0_generator(self):
        self.assertResult(True)

    @args("syntactes.generator", "SLRGenerator")
    def test_generator_exports_slr_generator(self):
        self.assertResult(True)

    @args("syntactes.generator", "LR1Generator")
    def test_generator_exports_lr1_generator(self):
        self.assertResult(True)


class TestRemovedModules(TestCase):
    def subject(self, module):
        return importlib.import_module(module)

    @args("syntactes.token")
    def test_token(self):
        self.assertResultRaises(ModuleNotFoundError)

    @args("syntactes.rule")
    def test_rule(self):
        self.assertResultRaises(ModuleNotFoundError)

    @args("syntactes.grammar")
    def test_grammar(self):
        self.assertResultRaises(ModuleNotFoundError)

    @args("syntactes.primitive")
    def test_primitive(self):
        self.assertResultRaises(ModuleNotFoundError)
