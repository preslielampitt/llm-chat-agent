import argparse
import os
import json
from groq import Groq
import glob
import readline
from .tools.calculate import calculate, calculate_tool_schema
from .tools.cat import cat, cat_tool_schema
from .tools.ls import ls, ls_tool_schema
from .tools.grep import grep, grep_tool_schema
from .tools.compact import compact, compact_tool_schema

from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = (
    "Write the output in 1-2 sentences. Always use tools when appropriate. "
    "Tools may only use relative paths inside the current working directory. "
    "Never use absolute paths or paths containing .. . When asked what a "
    "project does, first inspect README.md or the main source file. After "
    "reading enough information to answer, stop calling tools and give a final answer."
)


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

    '''
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.MODEL = 'openai/gpt-oss-120b'
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
        ]

    def send_message(self, message, temperature=0.8, debug=False):
        '''
        Send a user message to the language model, allow tool calls when needed, and return the final text response.

        This method adds the user's message to the conversation history, repeatedly handles tool calls until the model returns text, and stores the final assistant response in `self.messages`.
        '''
        self.messages.append({
            'role': 'user',
            'content': message
        })

        tools = [
            calculate_tool_schema,
            cat_tool_schema,
            ls_tool_schema,
            grep_tool_schema,
            compact_tool_schema,
        ]
        available_functions = {
            "calculate": calculate,
            "ls": ls,
            "cat": cat,
            "grep": grep,
            "compact": compact,
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
                    elif function_name == "compact":
                        print("[tool] /compact")

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
                elif function_name == "compact":
                    function_response = function_to_call(self.messages)
                    self.messages = [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "assistant",
                            "content": f"Conversation summary:\n{function_response}"
                        }
                    ]

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


COMMANDS = ['ls', 'cat', 'grep', 'calculate', 'compact']


def initialize_chat():
    '''
    Create a chat session for the current repository and preload AGENTS.md.
    >>> import os
    >>> import tempfile
    >>> old = os.getcwd()
    >>> with tempfile.TemporaryDirectory() as d:
    ...     os.chdir(d)
    ...     try:
    ...         initialize_chat()
    ...     except SystemExit:
    ...         pass
    ...     finally:
    ...         os.chdir(old)
    Error: this program must be run from a repository root containing a .git folder.
    >>> with tempfile.TemporaryDirectory() as d:
    ...     os.chdir(d)
    ...     os.mkdir('.git')
    ...     with open('AGENTS.md', 'w') as f:
    ...         _ = f.write('Use short answers.')
    ...     chat = initialize_chat()
    ...     'Use short answers.' in chat.messages[-1]['content']
    ...     os.chdir(old)
    True
    '''
    if not os.path.isdir('.git'):
        print('Error: this program must be run from a repository root containing a .git folder.')
        raise SystemExit(1)

    chat = Chat()

    if os.path.isfile('AGENTS.md'):
        agents_text = cat('AGENTS.md')
        chat.messages.append({
            'role': 'user',
            'content': 'Here are the repository instructions from AGENTS.md.'
        })
        chat.messages.append({
            'role': 'assistant',
            'content': agents_text
        })

    return chat


def command_completer(text, state):
    '''
    Return the next tab-completion match for slash commands or file paths.

    When the current input begins with `/`, this function suggests supported command names for the first token and matching file or directory names for later tokens.
    '''
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
    Run an interactive chat session that supports normal questions, slash commands, and optional debug output.

    The REPL reads user input in a loop, executes slash commands directly without calling the language model, and otherwise sends messages through the `Chat` object.

    >>> def monkey_input(prompt):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input

    >>> user_inputs=['/calculate 2+2']
    >>> repl()
    chat> /calculate 2+2
    4
    <BLANKLINE>

    >>> user_inputs=['/cat file_that_does_not_exist.txt']
    >>> repl()
    chat> /cat file_that_does_not_exist.txt
    File not found
    <BLANKLINE>

    >>> user_inputs=['/ls cmc_cs040_preslie']
    >>> repl(debug=True)  # doctest: +ELLIPSIS
    chat> /ls cmc_cs040_preslie
    [tool] /ls cmc_cs040_preslie
    ...
    <BLANKLINE>
    '''
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("bind ^I rl_complete")
    readline.set_completer(command_completer)
    chat = initialize_chat()
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
                    response = compact(chat.messages)
                    chat.messages = [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "assistant",
                            "content": f"Conversation summary:\n{response}"
                        }
                    ]
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
    '''
    Run the command-line entry point for the chat program.

    This function parses the `--debug` flag and an optional one-shot message from the command line, then either sends that message once or starts the interactive REPL.
    '''
    parser = argparse.ArgumentParser(description='Chat with the current project.')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='print tool calls while the chat runs'
    )
    parser.add_argument(
        'message',
        nargs='*',
        help='optional one-shot message to send to the chat'
    )

    args = parser.parse_args()

    if args.message:
        chat = initialize_chat()
        message = ' '.join(args.message)
        print(chat.send_message(message, debug=args.debug))
    else:
        repl(debug=args.debug)


if __name__ == '__main__':
    main()
