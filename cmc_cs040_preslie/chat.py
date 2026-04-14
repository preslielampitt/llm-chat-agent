import os
import json
from groq import Groq
import glob
import readline
import sys
from .tools.calculate import calculate, calculate_tool_schema
from .tools.cat import cat, cat_tool_schema
from .tools.ls import ls, ls_tool_schema
from .tools.grep import grep, grep_tool_schema

from dotenv import load_dotenv
load_dotenv()


class Chat:
    '''
    Chat stores a conversation history and sends user messages to the Groq API to generate responses.
    It can also let the model call tools such as `calculate`, `ls`, `cat`, and `grep` when they are useful for answering a question.
    The conversation history is saved in `self.messages` so the model can remember earlier context.

    >>> chat = Chat()
    >>> isinstance(chat.send_message('my name is Bob', temperature=0.0), str)
    True
    >>> response = chat.send_message('what is my name?', temperature=0.0)
    >>> 'bob' in response.lower()
    True

    >>> chat2 = Chat()
    >>> isinstance(chat2.send_message('what is my name?', temperature=0.0), str)
    True

    >>> chat = Chat()
    >>> chat.messages.append({'role': 'user', 'content': 'My name is Bob'})
    >>> summary = chat.compact()
    >>> isinstance(summary, str)
    True
    >>> len(chat.messages)
    2
    '''
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.MODEL = 'openai/gpt-oss-120b'
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences. Always use tools when appropriate. Tools may only use relative paths inside the current working directory. Never use absolute paths or paths containing .. . When asked what a project does, first inspect README.md or the main source file. After reading enough information to answer, stop calling tools and give a final answer."
            },
        ]

    def send_message(self, message, temperature=0.8, debug=False):
        self.messages.append({
            'role': 'user',
            'content': message
        })

        tools = [calculate_tool_schema, cat_tool_schema, ls_tool_schema, grep_tool_schema]
        available_functions = {
            "calculate": calculate,
            "ls": ls,
            "cat": cat,
            "grep": grep,
        }

        max_rounds = 5
        round_count = 0

        while round_count < max_rounds:
            round_count += 1
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model=self.MODEL,
                temperature=temperature,
                seed=0,
                tools=tools,
                tool_choice="auto",
            )

            response_message = chat_completion.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                result = response_message.content
                if result is None:
                    result = "I couldn't generate a final text response."
                self.messages.append({
                    'role': 'assistant',
                    'content': result
                })
                return result

            self.messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                if function_to_call is None:
                    continue

                function_args = json.loads(tool_call.function.arguments)

                if debug:
                    if function_name == "calculate":
                        print(f"[tool] /calculate {function_args.get('expression')}")
                    elif function_name == "ls":
                        print(f"[tool] /ls {function_args.get('folder')}")
                    elif function_name == "cat":
                        print(f"[tool] /cat {function_args.get('filename')}")
                    elif function_name == "grep":
                        print(f"[tool] /grep {function_args.get('pattern')} {function_args.get('path')}")

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

                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })
        result = "I couldn't generate a final text response."
        self.messages.append({
            'role': 'assistant',
            'content': result
        })
        return result
    

    def compact(self):
        summarizer = Chat()

        prompt = (
            "Summarize this conversation in 1-5 lines. "
            "Keep important facts, prior tool results, and user goals. "
            "Do not include unnecessary detail."
        )

        summary_messages = [
            {
                "role": "system",
                "content": prompt
            }
        ] + self.messages

        response = summarizer.client.chat.completions.create(
            model=self.MODEL,
            messages=summary_messages,
            temperature=0.0,
            seed=0,
        )

        summary = response.choices[0].message.content

        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences. Always use tools when appropriate. Tools may only use relative paths inside the current working directory. Never use absolute paths or paths containing .. . If information is already in the conversation history, answer from that context instead of calling a tool again."
            },
            {
                "role": "assistant",
                "content": f"Conversation summary:\n{summary}"
            }
        ]

        return summary


COMMANDS = ['ls', 'cat', 'grep', 'calculate', 'compact']


def command_completer(text, state):
    buffer = readline.get_line_buffer()
    parts = buffer.split()

    matches = []

    if buffer.startswith('/'):
        if len(parts) == 0:
            matches = [f'/{cmd}' for cmd in COMMANDS]
        elif len(parts) == 1 and not buffer.endswith(' '):
            prefix = parts[0][1:]
            matches = [f'/{cmd}' for cmd in COMMANDS if cmd.startswith(prefix)]
        else:
            if buffer.endswith(' '):
                path_prefix = ''
            else:
                path_prefix = parts[-1]

            matches = sorted(glob.glob(path_prefix + '*'))

            matches = [
                m + '/' if os.path.isdir(m) and not m.endswith('/') else m
                for m in matches
            ]

    try:
        return matches[state]
    except IndexError:
        return None


def repl(temperature=0.8, debug=False):
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

    >>> def monkey_input(prompt, user_inputs=['/ls cmc_cs040_preslie']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(debug=True)  # doctest: +ELLIPSIS
    chat> /ls cmc_cs040_preslie
    [tool] /ls cmc_cs040_preslie
    ...
    <BLANKLINE>
    '''
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("bind ^I rl_complete")
    readline.set_completer(command_completer)
    chat = Chat()
    try:
        while True:
            user_input = input('chat> ')

            if user_input.startswith('/'):
                parts = user_input[1:].split(maxsplit=1)
                command = parts[0]
                arg = parts[1] if len(parts) > 1 else None

                if debug:
                    if arg is None:
                        print(f'[tool] /{command}')
                    else:
                        print(f'[tool] /{command} {arg}')

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
                elif command == 'compact':
                    response = chat.compact()
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

            response = chat.send_message(user_input, temperature=temperature, debug=debug)
            print(response)
    except (KeyboardInterrupt, EOFError):
        print()


def main():
    debug = False
    args = sys.argv[1:]

    if '--debug' in args:
        debug = True
        args.remove('--debug')

    if args:
        chat = Chat()
        message = ' '.join(args)
        print(chat.send_message(message, debug=debug))
    else:
        repl(debug=debug)


if __name__ == '__main__':
    main()
