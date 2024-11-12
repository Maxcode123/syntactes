class ParserError(Exception): ...


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


class UnresolvableConflictError(ParserError):
    """
    An unresolvable conflict occured probable because of a nested operation
    with a token that cannot associate.

    e.g. x op y op z, if op cannot associate (has NO_ASSOCIATION associativity).
    """

    def __init__(self, token, actions):
        self.token = token
        self.action = actions
        msg = f"Cannot resolve conflict for actions {actions}; token {token} cannot associate. "
        super().__init__(msg)
