My project is a DisneyLand companion chat.

In this chat project, you can:
- Get recommendations to plan your day to maximize what you get to
- Customize your bucket list with different characters, shows, and rides
- Be in the know about the good food, from snacks and treats to dinner and lunch

The project will be governed by a Chat UI, that gets to decide which functions to call next to help out the user. This Chat will start by designing their bucket list by passing it to a Bucket List agent. This agent will have details about characters, shows, and rides, and will prompt the user with questions to find out what they most want to do. This bucket list will be saved for future reference. The Chat also has access to a Foodie agent, which will help the user decide where they want to eat their meals, and which snacks they want, including budgeting options. The last agent is the Ride Optimizer agent. With the user's bucket list in hand, as well as the ability to ask for additional information such as how many days they have, what they've done so far, what time it currently is, etc, it will call a python algorithm (which will be pre-written by an agent) to calculate what order they should do rides in. This algorithm will take in average wait times at different times of day, walking distance, character and show times, etc. 