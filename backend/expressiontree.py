def binaryoperator(ch: str) -> bool:
    return ch in {'&', '|', '*', '+'}

def unaryoperator(ch: str) -> bool:
    return ch in {'~', '!'}

class Node:
    def __init__(self, value: str):
        self.value = value
        self.left = None
        self.right = None

def exptree(exp: str) -> Node:
    stack = []
    for token in exp:
        if binaryoperator(token):
            node = Node(token)
            if len(stack) >= 2:
                right = stack.pop()
                left = stack.pop()
                node.left = left
                node.right = right
            stack.append(node)
        elif unaryoperator(token):
            node = Node(token)
            if stack:
                child = stack.pop()
                node.left = child
            stack.append(node)
        else:
            node = Node(token)
            stack.append(node)
    return stack[0] if stack else None
