# backend/tree_to_graph.py
from typing import List, Tuple
from backend.expressiontree import Node
from backend.gate_node import GateNode

def tree_to_graph(root: Node) -> Tuple[List[GateNode], GateNode]:
    node_map = {}
    id_counter = [0]

    def convert(node: Node) -> GateNode:
        if not node:
            return None
        if id(node) in node_map:
            return node_map[id(node)]

        gate_type = ""
        label = node.value

        if node.value in {'&', '*', '.'}:
            gate_type = "AND"
        elif node.value in {'|', '+'}:
            gate_type = "OR"
        elif node.value in {'~', '!'}:
            gate_type = "NOT"
        elif node.value in {'^'}:
            gate_type = "XOR"
        elif node.value in {'@'}:
            gate_type = "XNOR"
        elif node.value in {'>'}:
            gate_type = "IMPLIES"
        elif node.value in {'='}:
            gate_type = "EQUIV"
        else:
            gate_type = "INPUT"
            label = node.value  # A, B, C

        gate = GateNode(id_counter[0], gate_type, label)
        id_counter[0] += 1
        node_map[id(node)] = gate

        gate.left = convert(node.left)
        gate.right = convert(node.right)

        return gate

    root_gate = convert(root)
    all_nodes = list(node_map.values())
    return all_nodes, root_gate