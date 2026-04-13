import json 

def calculate(expression):
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)  # Use safe evaluation in production
        return str(result)
        #return json.dumps({"result": result})
    except:
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