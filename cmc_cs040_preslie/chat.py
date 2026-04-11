import os
import json
from groq import Groq
from .tools.calculate import calculate, tool_schema

from dotenv import load_dotenv
load_dotenv()

# in python class names are in CamelCase: 
# non-class names (e.g. function/variable) are in snake_case: 
class Chat:
    '''
    >>> chat = Chat()
    >>> chat.send_message('my name is Bob', temperature=0.0)
    'Nice to meet you, Bob!'
    >>> chat.send_message('what is my name?', temperature=0.0)
    'Your name is Bob.'

    >>> chat2 = Chat()
    >>> isinstance(chat2.send_message('what is my name?', temperature=0.0), str)
    True
    '''
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    def __init__(self):
        self.MODEL = 'openai/gpt-oss-120b'
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences. Always use tools to complete tasks when appropriate."
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
        tools = [tool_schema]  

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
            }
            
            # Add the assistant's response to conversation
            self.messages.append(response_message)
            
            # Step 3: Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    expression=function_args.get("expression")
                )
                print(f'[tool] function_name={function_name}, function_args={function_args}')
                
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


if __name__ == '__main__':
    repl()