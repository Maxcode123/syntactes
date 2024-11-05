import functools
from collections.abc import Callable
from typing import TypeAlias

from syntactes import Rule

Executable: TypeAlias = Callable[[...], None]


def execute_on(rule: Rule):
    """
    Decorate a function to be executed upon recognition of `rule` by the parser.
    """

    def executable_decorator(executable_fn: Executable) -> Executable:
        ExecutablesRegistry.register(rule, executable_fn)

        @functools.wraps(executable_fn)
        def wrapped_executable_fn(*args, **kwargs) -> None:
            return executable_fn(*args, **kwargs)

        return wrapped_executable_fn

    return executable_decorator


class ExecutablesRegistry:
    """
    Registry of executable functions, i.e. functions that get called when a grammar
    rule is recognized by the parser.
    """

    _registry: dict[Rule, Executable] = {}

    @classmethod
    def register(cls, rule: Rule, executable_fn: Executable) -> None:
        """
        Register a function to be executed upon recognition of the given rule.
        """
        cls._registry[rule] = executable_fn

    @classmethod
    def get(cls, rule: Rule) -> Executable:
        """
        Get the executable registered for the given rule.
        If no executable is registered returns a function that does nothing.
        """
        return cls._registry.get(rule, lambda *_, **__: None)

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered rules.
        """
        cls._registry.clear()
