# infix_to_postfix_full.py

def precedence(op):
    """Return operator precedence."""
    if op in ['!', '~']:      # NOT
        return 5
    elif op in ['&', '*']:    # AND
        return 4
    elif op == '^':           # XOR
        return 3
    elif op == '@':           # XNOR
        return 2
    elif op in ['|', '+']:    # OR
        return 1
    else:
        return 0

def is_operator(c):
    """Check if character is a valid operator."""
    return c in ['!', '~', '&', '*', '|', '+', '^', '@']

def infix_to_postfix(expression):
    stack = []    # operator stack
    output = []   # output list

    for ch in expression:
        if ch.isalpha():         # operands (A, B, C, ...)
            output.append(ch)

        elif ch == '(':
            stack.append(ch)

        elif ch == ')':
            # pop until '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # remove '('

        elif is_operator(ch):
            # handle NOT (right-associative)
            while (stack and stack[-1] != '(' and
                   ((precedence(stack[-1]) > precedence(ch)) or
                    (precedence(stack[-1]) == precedence(ch) and ch not in ['!', '~']))):
                output.append(stack.pop())
            stack.append(ch)

    while stack:
        output.append(stack.pop())

    return ''.join(output)


# -------------- MAIN --------------
if __name__ == "_main_":
    print("Operators supported: ! (NOT), & (AND), | (OR), ^ (XOR), @ (XNOR)")
    expr = input("Enter boolean expression: ")
    postfix = infix_to_postfix(expr.replace(" ", ""))  # remove spaces
    print("Postfix expression:", postfix)
