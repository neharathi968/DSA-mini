def is_operand(ch):
    return ('A' <= ch <= 'Z') or ('a' <= ch <= 'z')

def is_binary_operator(ch):
    return ch in ['&', '|', '*', '+']

def is_unary_operator(ch):
    return ch in ['~', '-']

def apply_binary_operator(op1, op2, ch):
    if ch in ['&', '*']:
        return op1 and op2
    elif ch in ['|', '+']:
        return op1 or op2

def apply_unary_operator(op):
    return not op

def evaluate_postfix(expression, truth_values):
    stack = []
    for ch in expression:
        if is_operand(ch):
            stack.append(truth_values[ch])
        elif is_binary_operator(ch):
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(apply_binary_operator(op1, op2, ch))
        elif is_unary_operator(ch):
            op = stack.pop()
            stack.append(apply_unary_operator(op))
        else:
            raise ValueError(f"Invalid character: {ch}")
    return stack.pop()

def generate_combinations(variables):
    combinations = []
    n = len(variables)
    for i in range(2 ** n):
        truth_values = {}
        for j in range(n):
            truth_values[variables[j]] = (i // (2 ** (n - j - 1))) % 2 == 1
        combinations.append(truth_values)
    return combinations

def evaluate_all(combinations, expression):
    results = []
    for truth_values in combinations:
        results.append(evaluate_postfix(expression, truth_values))
    return results

def truth_table(expression):
    variables = sorted(list(set(ch for ch in expression if is_operand(ch))))
    combinations = generate_combinations(variables)
    results = evaluate_all(combinations, expression)
    print(" | ".join(variables) + " | Result")
    print("-" * (4 * len(variables) + 9))
    for truth_values, result in zip(combinations, results):
        row = " | ".join(str(int(truth_values[var])) for var in variables)
        print(f"{row} |   {int(result)}")

if __name__ == "__main__":
    expr = input("Enter postfix expression: ")
    truth_table(expr)

    

            
