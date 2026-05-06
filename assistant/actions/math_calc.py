"""
MAZE — Math Calculator
Handles calculations from voice/text commands.
"""

import re
from assistant.actions.helpers import has_word


def handle_math(command: str) -> str:
    """Handle calculations."""
    expr = command
    for remove in ["calculate", "what is", "what's", "how much is", "solve", "equals"]:
        expr = expr.replace(remove, " ")

    math_words = {
        " plus ": "+", " add ": "+", " added to ": "+",
        " minus ": "-", " subtract ": "-", " subtracted from ": "-",
        " times ": "*", " multiply ": "*", " multiplied by ": "*", " into ": "*",
        " x ": "*", " × ": "*", " X ": "*",
        " divided by ": "/", " divide ": "/", " over ": "/",
        " power ": "**", " to the power of ": "**", " square ": "**2",
        " mod ": "%", " modulo ": "%", " remainder ": "%",
    }
    for word, op in math_words.items():
        expr = expr.replace(word, op)

    expr = expr.replace("x", "*").replace("×", "*").replace("X", "*")
    expr = ''.join(c for c in expr if c in '0123456789.+-*/() %')
    expr = expr.strip()
    expr = expr.strip('+-*/% ')

    if expr and any(c.isdigit() for c in expr):
        numbers = re.findall(r'\d+\.?\d*', expr)
        has_operator = any(op in expr for op in ['+', '-', '*', '/', '%', '**'])

        if len(numbers) < 2 or not has_operator:
            num = numbers[0] if numbers else expr
            return f"I heard '{command}'. Did you mean something like '{num} times 4' or '{num} plus 10'? Give me the full calculation."

        try:
            result = eval(expr)
            if isinstance(result, float) and result == int(result):
                result = int(result)
            return f"The answer is {result}."
        except:
            return "I couldn't calculate that. Try saying it like 'calculate 25 times 4'."
    return None
