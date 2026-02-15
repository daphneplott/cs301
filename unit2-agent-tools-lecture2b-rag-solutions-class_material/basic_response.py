# Before running this script:
# pip install gradio openai

import argparse
import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from usage import print_usage, format_usage_markdown

from chroma_demo import query_whole_documents

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

        rag = query_whole_documents('chroma','chroma_gc',user_message)

        self._history.append({'role':'system','content': "RAG: "+ str(rag)})

        stream = self._ai.responses.stream(
            input=self._history,
            model=self.model,
            reasoning=self.reasoning,
        )
        
        async with stream as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield 'output', event.delta

                if event.type == "response.reasoning_summary_text.delta":
                    yield 'reasoning', event.delta

            response = await stream.get_final_response()
            self.usage.append(response.usage)
            self.usage_markdown = format_usage_markdown(self.model, self.usage)
            self._history.extend(
                response.output
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)


async def _main_console(agent_args):
    with ChatAgent(**agent_args) as agent:
        
        message = input('User: ')

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

def main(prompt_path: Path, model: str, show_reasoning, reasoning_effort: str | None, use_web: bool):
    agent_args = dict(
        model=model,
        prompt=prompt_path.read_text() if prompt_path else '',
        show_reasoning=show_reasoning,
        reasoning_effort=reasoning_effort

    )

    asyncio.run(_main_console(agent_args))


# Launch app
if __name__ == "__main__":
    parser = argparse.ArgumentParser('ChatBot')
    parser.add_argument('prompt_file', nargs='?', type=Path, default='system_prompt.md')
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--show-reasoning', action='store_true')
    parser.add_argument('--reasoning-effort', default='low')
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning, args.reasoning_effort, args.web)