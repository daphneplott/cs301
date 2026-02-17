# Before running this script:
# pip install gradio openai

import argparse
import asyncio
import json
import random
import requests
from pathlib import Path

import gradio as gr
from openai import AsyncOpenAI

from tools import ToolBox
from usage import print_usage, format_usage_markdown
from basic_response import get_a_response

our_tools = ToolBox()


@our_tools.tool
def get_random_number(lower: int, upper: int) -> int:
    """Get a random number"""
    return random.randint(lower, upper)

@our_tools.tool
def web_tool(url: str, just_link: bool = True, speaker: str = "") -> tuple[str,str|None]:
    """
    Fetches the content of a web page from the given URL. If just_link is true, it will only return
    a single link from the page, which corresponds to speaker. If just_link is false, it will return   
    the entire HTML page. 
    
    Args:
        url (str): The URL to fetch.
        just_link (bool): Determines if the function returns the entire page, or a single url
        speaker (str): The name of the speaker
    
    Returns:
        str: The HTML/text content of the page, or the next link
        str: Usage data
    
    Raises:
        ValueError: If the URL is invalid or empty.
        requests.RequestException: For network-related errors.
    """
    # Validate input
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string.")
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with 'http://' or 'https://'.")

    try:
        # Send GET request with a timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        if just_link:
            return get_a_response([{'role':'system', 'content': f'Pull out the link from this page that leads to the speaker {speaker}: {response.text}'}])
        return response.text, None
    
    except requests.exceptions.Timeout:
        raise requests.RequestException("Request timed out.")
    except requests.exceptions.ConnectionError:
        raise requests.RequestException("Failed to connect to the server.")
    except requests.exceptions.HTTPError as e:
        raise requests.RequestException(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        raise requests.RequestException(f"An error occurred: {e}")


class ChatAgent:
    def __init__(self, model: str, prompt: str, show_reasoning: bool, reasoning_effort: str | None):
        self._ai = AsyncOpenAI()
        self.model = model
        self.show_reasoning = show_reasoning
        self.reasoning = {}
        if show_reasoning:
            self.reasoning['summary'] = 'auto'
        if 'gpt-5' in self.model and reasoning_effort:
            self.reasoning['effort'] = reasoning_effort

        self.usage = []
        self.usage_markdown = format_usage_markdown(self.model, [])

        self._history = []
        self._prompt = prompt
        if prompt:
            self._history.append({'role': 'system', 'content': prompt})

    async def get_response(self, user_message: str):
        self._history.append({'role': 'user', 'content': user_message})

        while True:
            response = await self._ai.responses.create(
                input=self._history,
                model=self.model,
                reasoning=self.reasoning,
                tools=our_tools.tools
            )

            self.usage.append(response.usage)
            self.usage_markdown = format_usage_markdown(self.model, self.usage)
            self._history.extend(
                response.output
            )

            for item in response.output:
                if item.type == 'reasoning':
                    for chunk in item.summary:
                        yield 'reasoning', chunk.text

                elif item.type == 'function_call':
                    yield 'reasoning', f'{item.name}({item.arguments})'

                    func = our_tools.get_tool_function(item.name)
                    args = json.loads(item.arguments)
                    result = func(**args)
                    if func == web_tool:
                        if result[1] != None:
                            self.usage.append(result[1])
                    self._history.append({
                        'type': 'function_call_output',
                        'call_id': item.call_id,
                        'output': str(result)
                    })
                    yield 'reasoning', str(result)[:100]

                elif item.type == 'message':
                    for chunk in item.content:
                        yield 'output', chunk.text
                    return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)


async def _main_console(agent_args):
    with ChatAgent(**agent_args) as agent:
        while True:
            message = input('User: ')
            if not message:
                break

            reasoning_complete = True
            if agent.show_reasoning:
                print(' Reasoning '.center(30, '-'))
                reasoning_complete = False

            async for text_type, text in agent.get_response(message):
                if text_type == 'output' and not reasoning_complete:
                    print()
                    print('-' * 30)
                    print()
                    print('Agent: ')
                    reasoning_complete = True

                print(text, end='', flush=True)
            print()
            print()


def _main_gradio(agent_args):
    # Constrain width with CSS and center
    css = """
    /* limit overall Gradio app width and center it */
    .gradio-container, .gradio-app, .gradio-root {
      width: 120ch;
      max-width: 120ch !important;
      margin-left: auto !important;
      margin-right: auto !important;
      box-sizing: border-box !important;
    }
    
    #reasoning-md {
        max-height: 300px;
        overflow-y: auto;
    }
    """

    reasoning_view = gr.Markdown('', elem_id='reasoning-md')
    usage_view = gr.Markdown('')

    with gr.Blocks(css=css, theme=gr.themes.Monochrome()) as demo:
        agent = gr.State()

        async def get_response(message, chat_view_history, agent):
            output = ""
            reasoning = ""

            async for text_type, text in agent.get_response(message):
                if text_type == 'reasoning':
                    reasoning += text
                elif text_type == 'output':
                    output += text
                else:
                    raise NotImplementedError(text_type)

                yield output, reasoning, agent.usage_markdown, agent

            yield output, reasoning, agent.usage_markdown, agent

        with gr.Row():
            with gr.Column(scale=5):
                bot = gr.Chatbot(
                    label=' ',
                    height=600,
                    resizable=True,
                )
                chat = gr.ChatInterface(
                    chatbot=bot,
                    fn=get_response,
                    additional_inputs=[agent],
                    additional_outputs=[reasoning_view, usage_view, agent]
                )

            with gr.Column(scale=1):
                reasoning_view.render()
                usage_view.render()

        demo.load(fn=lambda: ChatAgent(**agent_args), outputs=[agent])

    demo.launch()


def main(prompt_path: Path, model: str, show_reasoning, reasoning_effort: str | None, use_web: bool):
    agent_args = dict(
        model=model,
        prompt=prompt_path.read_text() if prompt_path else '',
        show_reasoning=show_reasoning,
        reasoning_effort=reasoning_effort

    )

    if use_web:
        _main_gradio(agent_args)
    else:
        asyncio.run(_main_console(agent_args))


# Launch app
if __name__ == "__main__":
    parser = argparse.ArgumentParser('ChatBot')
    parser.add_argument('prompt_file', nargs='?', type=Path, default=None)
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--show-reasoning', action='store_true')
    parser.add_argument('--reasoning-effort', default='low')
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning, args.reasoning_effort, args.web)
