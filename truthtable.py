#creating a truth table of a given postfix expression

def operand(char):
    if char>='A' and char <= 'Z' or char>='a' and char<='z':
        return True
    return False

def binaryoperator(char):
    if char == '&' or char == '|' or char == '*' or char == '+': 
        return True
    return False

def uniraryoperator(char):
    if char == '~' or char == '-': 
        return True
    return False

def applybinaryoperator(op1,op2,char):
    if char == '&':
        return op1 and op2
    elif char == '*':
        return op1 and op2
    elif char == '|':
        return op1 or op2
    elif char == '+':
        return op1 or op2

def applyuniraryoperator(op):
    return not op

    


def evaluation_of_postfix(exp, truth_values):
    stack = []
    for char in exp:
        if operand(char):
            stack.append(truth_values[char])  # Push the truth value of the operand
        elif binaryoperator(char):
            op2 = stack.pop()
            op1 = stack.pop()
            result = applybinaryoperator(op1, op2, char)
            stack.append(result)
        elif uniraryoperator(char):
            op = stack.pop()
            result = applyuniraryoperator(op)
            stack.append(result)
        else:
            raise ValueError(f"Invalid character in expression: {char}")
    return stack.pop()

def generate_combination(variables):
    values = [False, True]
    combinations = []
    n = len(variables)
    for i in range(2 ** n):
        truth_value = {}
        for j in range(n):
            truth_value[variables[j]] = (i // (2 ** (n - j - 1))) % 2 == 1
        combinations.append(truth_value)
    return combinations

def evaluate_result(combinations,exp):
    results = []
    for truth_value in combinations:
        result = evaluation_of_postfix(exp,truth_value)
        results.append(result)
    return results

def truthtable(exp):  #exp = a postfix expression(ab&c|)
    list_of_var = []
    for char in exp:
        if operand(char):
            list_of_var.append(char)
    list_of_var = list(set(list_of_var))
    list_of_var.sort()
    #Generating all combinations
    combinations = generate_combination(list_of_var)
  
    # Evaluate the results for the postfix expression
    results = evaluate_result(combinations, exp)

    # Print the header of the truth table
    print(" | ".join(list_of_var) + " | Result")
    print("-" * (4 * len(list_of_var) + 9))

    # Print each row of the truth table
    for truth_value, result in zip(combinations, results):
        row = " | ".join(str(int(truth_value[var])) for var in list_of_var)
        print(f"{row} |   {int(result)}")

# Example usage
expression = "ab&c|"
truthtable(expression)

    

            
