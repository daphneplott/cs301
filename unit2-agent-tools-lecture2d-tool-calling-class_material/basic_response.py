from time import time

from openai import Client

from usage import print_usage

from matplotlib import pyplot as plt

import json


def get_a_response(message):
    client = Client()
    model = 'gpt-5-nano'
    response = client.responses.create(
        model=model,
        input= message ,
        reasoning={'effort': 'minimal'}
    )
    return response.output_text, response.usage


if __name__ == '__main__':
    get_a_response("Hello")
