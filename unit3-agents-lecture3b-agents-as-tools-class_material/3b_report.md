Build a chat that has both input and output guardrails
When a user mentions a taboo topic, the prompt gets additional emphasis on how to respond
When the agent returns data that is invalid/incorrect, the agent is prompted with the feedback to try again.

The first idea I had for the gaurdrails was to design two agents. One of them would be a basic agent, and it would function as a tool for the main agent. The main agent would be in charge of screening the input and output, and communicating with the basic agent. 

However, as I was starting to implement it, I realized I was going to have problems keeping the chat bot's memory, so I decided to switch the roles. I gave the chatbot two functions, one to screen the input and offer emphasis about taboo topics, and one to screen the output and give feedback. As I was writing it, I had a hard time getting the chat bot to call the input screener. I think the problem was that the prompting for that was much less significant than the output screener. I wonder if the agent thought that it was just fine without an input screener.

One thing I liked about this system was that I felt like the secret keeping was better when I could have one agent with each goal. I felt like it was the equivalent of talking something out with someone else because they usually are thinking about things differently than you. However, it did cost a lot more money, even with the nano versions.

The taboo topic I chose was rubber ducks, as well as a secret password Coco Loco

Question:
- Does letting the chat bot know it's being gaurded by a bot help?
