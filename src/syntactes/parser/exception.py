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
