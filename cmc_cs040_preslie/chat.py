import os
import json
from groq import Groq
from .tools.calculate import calculate, calculate_tool_schema
from .tools.cat import cat, cat_tool_schema
from .tools.ls import ls, ls_tool_schema
from .tools.grep import grep, grep_tool_schema

from dotenv import load_dotenv
load_dotenv()

# in python class names are in CamelCase: 
# non-class names (e.g. function/variable) are in snake_case: 
class Chat:
    '''
    >>> chat = Chat()
    >>> isinstance(chat.send_message('my name is Bob', temperature=0.0), str)
    True
    >>> response = chat.send_message('what is my name?', temperature=0.0)
    >>> 'bob' in response.lower()
    True

    >>> chat2 = Chat()
    >>> isinstance(chat2.send_message('what is my name?', temperature=0.0), str)
    True
    '''
    #client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.MODEL = 'openai/gpt-oss-120b'
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences. Always use tools when appropriate, but if the needed information is already in the conversation history, answer from that context instead of calling a tool again."
            },
        ]
    def send_message(self, message, temperature=0.8):
        self.messages.append(
            {
                # system: never change; user: changes a lot 
                # the message that you are sending to the AI
                'role': 'user', 
                'content': message
            }
        )
        tools = [calculate_tool_schema, cat_tool_schema, ls_tool_schema, grep_tool_schema]  

        # in order to make non deterministic code deterministic: 
        # in this case, has a 'temperature' param that controls randomness: 
        # the higher the value, the more randomness; 
        # higher temperature = more creativity
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            #model="llama-3.1-8b-instant",
            model=self.MODEL,
            temperature=temperature,
            seed=0,
            tools=tools,
            tool_choice="auto",
        )

        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls
        
        # Step 2: Check if the model wants to call tools
        if tool_calls:
            # Map function names to implementations
            available_functions = {
                "calculate": calculate,
                "ls": ls,
                "cat": cat,
                "grep": grep,
            }
            
            # Add the assistant's response to conversation
            self.messages.append(response_message)
            
            # Step 3: Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                if function_to_call is None:
                    continue

                function_args = json.loads(tool_call.function.arguments)

                if function_name == "calculate":
                    function_response = function_to_call(
                        expression=function_args.get("expression")
                    )
                elif function_name == "ls":
                    function_response = function_to_call(
                        folder=function_args.get("folder")
                    )
                elif function_name == "cat":
                    function_response = function_to_call(
                        filename=function_args.get("filename")
                    )
                elif function_name == "grep":
                    function_response = function_to_call(
                        pattern=function_args.get("pattern"),
                        path=function_args.get("path")
                    )

                #print(f'[tool] function_name={function_name}, function_args={function_args}')
                
                # Add tool response to conversation
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

            # Step 4: Get final response from model
            second_response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.messages
            ) 
            result = second_response.choices[0].message.content
            self.messages.append({
                'role': 'assistant',
                'content': result
            })
        else:
            result = chat_completion.choices[0].message.content
            self.messages.append({
                'role': 'assistant',
                'content': result
            })
        return result

def repl(temperature=0.8):
    '''
    >>> def monkey_input(prompt, user_inputs=['/calculate 2+2']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl()
    chat> /calculate 2+2
    4
    <BLANKLINE>

    >>> def monkey_input(prompt, user_inputs=['/cat file_that_does_not_exist.txt']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> builtins.input = monkey_input
    >>> repl()
    chat> /cat file_that_does_not_exist.txt
    File not found
    <BLANKLINE>
    '''
    import readline
    chat = Chat()
    try:
        while True:
            user_input = input('chat> ')

            if user_input.startswith('/'):
                parts = user_input[1:].split(maxsplit=1)
                command = parts[0]
                arg = parts[1] if len(parts) > 1 else None

                if command == 'ls':
                    response = ls(arg)
                elif command == 'cat':
                    response = cat(arg)
                elif command == 'calculate':
                    response = calculate(arg)
                elif command == 'grep':
                    if arg is None:
                        response = 'Usage: /grep <pattern> <path>'
                    else:
                        grep_parts = arg.split(maxsplit=1)
                        if len(grep_parts) < 2:
                            response = 'Usage: /grep <pattern> <path>'
                        else:
                            response = grep(grep_parts[0], grep_parts[1])
                else:
                    response = 'Unknown command'

                print(response)

                chat.messages.append({
                    'role': 'user',
                    'content': user_input
                })
                chat.messages.append({
                    'role': 'assistant',
                    'content': str(response)
                })
                continue
            
            if chat is None:
                chat = Chat()

            response = chat.send_message(user_input, temperature=temperature)
            print(response)
    except (KeyboardInterrupt, EOFError):
        print()

'''
# repl: reads input and evaluates input
def repl(temperature=0.8):
    import readline
    chat = Chat()
    try:
        while True:
            user_input = input('chat> ')
            response = chat.send_message(user_input, temperature = temperature)
            print(response)
    except (KeyboardInterrupt, EOFError):
        print()
'''


if __name__ == '__main__':
    repl()