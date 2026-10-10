from syntactes.primitive import Primitive
from syntactes.rule import Rule


class ParserError(Exception):
    """
    Base class of the errors raised by `parse()`.
    """


class UnexpectedTokenError(ParserError):
    """
    A token was received that does not map to an action. The stream of tokens
    is syntactically invalid.
    """

    def __init__(self, received_token, expected_tokens):
        self.received_token = received_token
        self.expected_tokens = expected_tokens
        msg = f"Received token: {received_token}; expected one of: {[str(e) for e in expected_tokens]}"
        super().__init__(msg)


class NotAcceptedError(ParserError):
    """
    The parser did not receive an accept action. The stream of tokens is
    syntactically invalid.
    """


class PrimitiveError(ParserError):
    """
    A rule's primitive raised while the parser applied it, e.g. `int` on a
    token whose value isn't a number. The rule and primitive are available as
    `rule` and `primitive`, and the original exception as `__cause__`.
    """

    def __init__(self, rule: Rule, primitive: Primitive) -> None:
        self.rule = rule
        self.primitive = primitive
        super().__init__(f"Primitive {primitive.string()} of rule '{rule}' failed.")
