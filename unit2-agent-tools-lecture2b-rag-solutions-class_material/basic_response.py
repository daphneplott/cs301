# Before running this script:
# pip install gradio openai

import argparse
import asyncio
from pathlib import Path

from openai import Client

from usage import print_usage, format_usage_markdown

from chroma_demo import query_whole_documents

class ChatAgent:
    def __init__(self, model: str, prompt: str, show_reasoning: bool, reasoning_effort: str | None):
        self._ai = Client()
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

    def get_response(self, user_message: str):
        self._history.append({'role': 'user', 'content': user_message})

        # pre_response = self._ai.responses.create(
        #     input=[{'role':'system', 'content': Path('summary_prompt.md').read_text()},{'role':'user','content':user_message}],
        #     model=self.model,
        #     reasoning=self.reasoning,
        # )

        # self.usage.append(pre_response.usage)
        # print("Summary: ", pre_response.output_text)
        # print()
        rag = query_whole_documents('chroma','chroma_gc',user_message)

        i = 1
        for doc in rag:
            print("Document: ", i)
            i += 1
            print(doc[:300])
            print()

        self._history.append({'role':'system','content': "RAG: "+ str(rag)})

        response = self._ai.responses.create(
            input=self._history,
            model=self.model,
            reasoning=self.reasoning,
        )

        self.usage.append(response.usage)


        print(response.output_text)
        

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print_usage(self.model, self.usage)


def _main_console(agent_args):
    with ChatAgent(**agent_args) as agent:
        
        message = input('User: ')
        agent.get_response(message)


def main(prompt_path: Path, model: str, show_reasoning, reasoning_effort: str | None, use_web: bool):
    agent_args = dict(
        model=model,
        prompt=prompt_path.read_text() if prompt_path else '',
        show_reasoning=show_reasoning,
        reasoning_effort=reasoning_effort

    )

    _main_console(agent_args)


# Launch app
if __name__ == "__main__":
    parser = argparse.ArgumentParser('ChatBot')
    parser.add_argument('prompt_file', nargs='?', type=Path, default='system_prompt_with_rag.md')
    parser.add_argument('--web', action='store_true')
    parser.add_argument('--model', default='gpt-5-nano')
    parser.add_argument('--show-reasoning', action='store_true')
    parser.add_argument('--reasoning-effort', default='low')
    args = parser.parse_args()
    main(args.prompt_file, args.model, args.show_reasoning, args.reasoning_effort, args.web)