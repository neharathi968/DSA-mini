# backend/gate_node.py
from typing import Optional

class GateNode:
    def __init__(self, id: int, type: str, label: Optional[str] = None):
        self.id = id
        self.type = type
        self.label = label or type
        self.left: Optional['GateNode'] = None
        self.right: Optional['GateNode'] = None

    def __repr__(self):
        return f"GateNode(id={self.id}, type='{self.type}', label='{self.label}')"