# backend/graph_to_reactflow.py
from collections import deque
import json
import os
from typing import Dict, Any
from backend.gate_node import GateNode

def _gate_label(gate: GateNode) -> str:
    if gate.type == "INPUT":
        return gate.label
    return gate.type

def graph_to_reactflow_json(root: GateNode) -> Dict[str, Any]:
    if not root:
        return {"nodes": [], "edges": []}

    nodes = []
    edges = []
    visited = set()
    queue = deque([(root, 0)])
    level_y = {}
    max_level = 0  # Track maximum depth

    # First pass: determine max depth
    temp_queue = deque([(root, 0)])
    temp_visited = set()
    while temp_queue:
        gate, level = temp_queue.popleft()
        if gate.id in temp_visited:
            continue
        temp_visited.add(gate.id)
        max_level = max(max_level, level)
        if gate.left:
            temp_queue.append((gate.left, level + 1))
        if gate.right:
            temp_queue.append((gate.right, level + 1))

    # Second pass: build nodes with reversed x positions
    while queue:
        gate, level = queue.popleft()
        if gate.id in visited:
            continue
        visited.add(gate.id)

        # Layout
        if level not in level_y:
            level_y[level] = []
        y = len(level_y[level]) * 140
        level_y[level].append(y)
        
        # REVERSED: inputs (high level) get low x, output (level 0) gets high x
        x = (max_level - level) * 300

        # Node type
        if gate.type == "INPUT":
            node_type = "input"
        else:
            node_type = gate.type  # Use actual gate type

        nodes.append({
            "id": str(gate.id),
            "type": node_type,
            "data": {"label": _gate_label(gate)},
            "position": {"x": x, "y": y},
            "style": {"fontWeight": "bold", "fontSize": 14}
        })

        # Add edges
        if gate.left:
            edges.append({
                "id": f"e{gate.left.id}-{gate.id}",
                "source": str(gate.left.id),
                "target": str(gate.id),
                "animated": True
            })
            queue.append((gate.left, level + 1))
        if gate.right:
            edges.append({
                "id": f"e{gate.right.id}-{gate.id}",
                "source": str(gate.right.id),
                "target": str(gate.id),
                "animated": True
            })
            queue.append((gate.right, level + 1))

    return {"nodes": nodes, "edges": edges}


def save_circuit_json(root: GateNode, filename: str = None) -> str:
    import uuid
    os.makedirs("static", exist_ok=True)
    filename = filename or f"static/circuit_{uuid.uuid4().hex}.json"
    data = graph_to_reactflow_json(root)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    return f"/static/{os.path.basename(filename)}"