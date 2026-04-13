import json


def calculate(expression):
    '''
    Evaluate a mathematical expression

    >>> calculate('4*4')
    '16'
    >>> calculate ('2+')
    '{"error": "Invalid expression"}'
    '''
    try:
        result = eval(expression)
        return str(result)
    except Exception:
        return json.dumps({"error": "Invalid expression"})


calculate_tool_schema = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
}
