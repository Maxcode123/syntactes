from enum import StrEnum


class AstNodeType(StrEnum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    NONE = "NONE"


class AstNode:
    node_type: AstNodeType
    literal: str

    def __init__(self, node_type: AstNodeType, literal: str) -> None:
        self.node_type = node_type
        self.literal = literal
