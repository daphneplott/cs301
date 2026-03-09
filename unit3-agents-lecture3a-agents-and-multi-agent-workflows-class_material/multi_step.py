from pathlib import Path

import yaml
from openai import AsyncOpenAI

from run_agent import run_agent
from tools import ToolBox
from usage import print_usage

toolbox = ToolBox()


async def main(agent_config: Path, message: str):
    client = AsyncOpenAI()

    config = yaml.safe_load(agent_config.read_text())
    agents = {agent['name']: agent for agent in config['agents']}

    history = []
    usage = []


    response = await run_agent(
        client, toolbox, agents['chat'],
        message, history, usage
    )

    print("Initial: ", response)

    second_result = await run_agent(
        client, toolbox, agents['topic_picker'],
        response, [], usage
    )

    print("Second: ",second_result)

    third_result = await run_agent(
        client, toolbox, agents['question_stubber'],
        second_result, [], usage
    )

    print("Third: ", third_result)

    final_result = await run_agent(
        client, toolbox, agents['theory_writer'],
        third_result, [], usage
    )

    print('Agent:', final_result)
    print()
    
    print_usage(agents['chat']['model'], usage)


if __name__ == '__main__':
    import sys
    import asyncio

    asyncio.run(main(Path(sys.argv[1]), sys.argv[2]))
