import re

def eval_postfix(tokens, valuation):
    if isinstance(tokens, str):
        tokens = list(tokens.strip().replace(" ", ""))
    elif isinstance(tokens, (list, tuple)):
        tokens = [t.strip() for t in tokens if t.strip()]
    else:
        raise TypeError("Postfix input must be a string or list of tokens")

    stack = []

    for tok in tokens:
        if not tok or tok.isspace():
            continue

        if re.fullmatch(r"[A-Za-z]", tok):
            stack.append(bool(valuation.get(tok, False)))
        elif tok in ('~', '!'):
            if not stack:
                raise ValueError("Malformed postfix: missing operand for NOT")
            a = stack.pop()
            stack.append(not a)
        elif tok in ('&', '.', '*'):
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for AND")
            b = stack.pop(); a = stack.pop()
            stack.append(a and b)
        elif tok in ('|', '+'):
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for OR")
            b = stack.pop(); a = stack.pop()
            stack.append(a or b)
        elif tok == '^':
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for XOR")
            b = stack.pop(); a = stack.pop()
            stack.append(bool(a) ^ bool(b))
        elif tok == '@':
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for XNOR")
            b = stack.pop(); a = stack.pop()
            stack.append(not (bool(a) ^ bool(b)))
        elif tok == '>':
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for IMPLIES")
            b = stack.pop(); a = stack.pop()
            stack.append((not a) or b)
        elif tok == '=':
            if len(stack) < 2:
                raise ValueError("Malformed postfix: missing operands for EQUIV")
            b = stack.pop(); a = stack.pop()
            stack.append(a == b)
        else:
            raise ValueError(f"Unknown token '{tok}'")

    if len(stack) != 1:
        raise ValueError("Invalid postfix expression (stack length != 1 at end)")

    return bool(stack[0])
