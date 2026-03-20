For my homework, I wanted to experiment with letting chat-bot style agents be able to use and read skills the way codex could. Professor Bean suggested in class this was an acceptable use of homework time.

The first thing I did was write a load_skill function, which takes in a skill file name, appends it to the current file path, and returns the file contents. I then gave the specific file name to the agent as part of the prompt, with instructions on when to call it, and which tool to use to do that.

The first time I ran it, I ended up with the agent loading the skill before it should have. It ignored the first response, because I think it realized it wasn't ready. However, when it loaded the skill when it was actually supposed to, it worked better.

