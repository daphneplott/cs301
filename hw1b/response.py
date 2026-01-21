import argparse
import sys
from pathlib import Path
from time import time

from openai import OpenAI
from pydantic import BaseModel, Field

from usage import print_usage

class Classification(BaseModel):
    style: str = Field(description="The style in which the paragraph is written.")
    score: int = Field(description="How effectively the paragraph uses that style")

class ClassificationList(BaseModel):
    classifications: list[Classification] = Field(description="A list of each classification")

def main(model: str, prompt: str,input_file:str):
    client = OpenAI()
    start = time()
    input = prompt + input_file
    response = client.responses.parse(
        model=model,
        input=input,
        #text_format =ClassificationList,
        reasoning={'effort': 'low'}
    )
    print(response.output_text)

    print(f'{round(time()-start, 2)} seconds elapsed', file=sys.stderr)
    print_usage(model, response.usage)


# Launch app
if __name__ == "__main__":
    parser = argparse.ArgumentParser('AI Response')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('input_file', type=Path)
    parser.add_argument('--model', default='gpt-5-nano')
    args = parser.parse_args()
    main(args.model, args.prompt_file.read_text(),args.input_file.read_text())
