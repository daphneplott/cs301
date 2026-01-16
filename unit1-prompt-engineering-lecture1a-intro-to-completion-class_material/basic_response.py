from time import time

from openai import Client

from usage import print_usage


def main():
    client = Client()
    start = time()
    model = 'gpt-5-nano'
    response = client.responses.create(
        model=model,
        input="Pretend you are are an ancient Roman. Give me five paragaphs about various topics." ,
        reasoning={'effort': 'low'}
    )
    print(f'Took {round(time() - start, 2)} seconds')
    print_usage(model, response.usage)
    print(response.output_text)


if __name__ == '__main__':
    main()
