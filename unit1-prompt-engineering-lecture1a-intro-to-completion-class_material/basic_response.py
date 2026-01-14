from time import time

from openai import Client

from usage import print_usage


def main():
    client = Client()
    start = time()
    model = 'gpt-4.1'
    response = client.responses.create(
        model=model,
        input="Are Thrass and Thrawn biologically related" ,
        #reasoning={'effort': 'low'}
    )
    print(f'Took {round(time() - start, 2)} seconds')
    print_usage(model, response.usage)
    print(response.output_text)


if __name__ == '__main__':
    main()
