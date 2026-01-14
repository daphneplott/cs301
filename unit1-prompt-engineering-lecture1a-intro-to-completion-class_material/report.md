# Homework 1a
## Daphne Plott

### 2
Prompts: 

Tell me a fact about cats

Write code that computes the fibonacci sequence

### 3

Can you identify the time of the model's knowledge cutoff?

To investigate this question, I started by asking the model "Tell me about a recent event". It then responded that I wasn't being specific enough, so I refined my prompt to "Tell me about a recent event in US entertainment according to your last update time". I found that the gpt-5-nano only has information up to June 2024. It was also very forthcoming with that information, so then I changed my prompt to "What time does your knowledge go up to?". The gpt-5.2 model is up to August 2025, and gpt-4.1 is up to June 2024 (and doesn't support reasoning). I learned that I can't expect to be able to use super recent events in my APIs. I also learned to just ask the question I want first.

Can it do math? What about higher level math, like Calculus, or low level proofs?

I put in an old AP calculus problem into gpt-5-nano. It was able to work through the story problem to solve it. It also went to the effort to not just give an answer, but explain it to me. I then ran the same prompt on gpt-5.2 and gpt-4.1. They all started out with about the same solution, but when it came to finish solving algebraically, they all did something sort of different. Gpt-5-nano just told me what it was, gpt-5.2 approximated quickly, and gpt-4.1 went through a lot of approximation steps. The two larger models cost a lot more for not doing that much more. They did, though, both output their answers in Latex, which I thought was interesting. All the models seem to be fairly competent at doing math like this.

I next ran the models to give me proofs of two simple concepts covered in Math 290. For the first prompt, which was a simpler proof, they all produced basically identical proofs. The 5.2 and 4.1 models formatted their answers in Latex, which is in general useful, but they also cost a lot more money. They did give a little more background and in between steps, but I'm not sure it's enough of a difference. I did notice that the 5.2 model worked faster than the 4.1 model. For the second prompt, which dealt with more complex topics, the 5.2 and 4.1 models produced something almost identical. The 5-nano model was similar, but didn't create as formal of a proof. As a grader, I would've had some notes for 5-nano (not necessarily a worse grade, but notes), but not for the other two models. However, the other two models cost a lot more money. I'm impressed that the models can manage proofs like this. However, I also expect that a lot of this information is out on the web, somewhere. The smaller models still seem to return the right information, but don't offer as much explanation or formality as some of the more advanced models.


Does it know the details of those obscure books you read as a teenager?

I started with a more broad prompt of "Tell me about the book Thrawn Ascendency". They all came up with most of the same facts, but with some differences. The 4.1 model included a few more character details, but got a character name wrong. The 4.1 model also takes a lot longer. The 5-nano was sufficient for this question. 

I then asked a more specific question of "Who's Thrawn's brother?" (which is much more niche). The 5-nano wasn't able to figure it out, 5.2 got the name, but was wrong about the context, and the 4.1 was correct. I changed the prompt to "Tell me about Thrass from Star Wars." 5-nano struggled to find the character. Even when I gave it additional information, it couldn't find the Outbound Flight details the other two models did. 4.1 and 5.2 gave very similar responses, but were both wrong about the fact that Thrass doesn't come back in more recent books. I then added "from Thrawn Ascendency, Lesser Evil" to my prompt (which is the newest book including Thrass), and 5-nano still couldn't find it. I then changed the prompt to  "Are Thrass and Thrawn biologically related" to see if the models could actually find information from the newest book. 4.1 DID find the right answer, but 5.2 did NOT, surprisingly. I ran both a few more times on the same input. The 5.2 consistently was wrong, and changed its opinion about who was older. The 4.1 was still right about the main question, but was sometimes right and sometimes wrong about supporting details. I learned that the models aren't as good as picking out niche information, and that you really can't always trust what the models say. I also got to see firsthand how the models are nondeterminate, sometimes. But they never tell you how confident they are about certain things, which is something I'll have to look out for.

Can it produce different styles? How well?

My first prompt was "Write an informative paragraph about the history of pirates in the style of a pirate." The 5-nano model didn't seem to catch on to some of the smaller historical facts, but I felt had the best styling overall. The 5.2 seemed to do the worst at being piratey. It started out really well, but sort of lost it besides from the occasional slang word. I then had it do the same thing for Shakespeare. The 4.1 seemed the most poetic, and the styling of the other two were more just old english than Shakesperian. It was interesting that they focused on different parts of the information of Shakespeare. The 5-nano focused on his plays, the 5.2 on his life, and the 4.1 on his impact. I think that sometimes the prompts are openended enough for the models to come to differen conclusions, even when they are usually very similar.


Does it understand LDS theology, and how does it speak about it?

I used the prompt "Tell me about the doctrine in The Family: A Proclamation to the world." For the 5-nano, it reconized it was LDS, and gave a good summary, which seemed fairly neutral in tone. The 5.2 also gave a good summary, and included more associations in the gospel. It also seemed fairly neutral. The 4.1 gave a good summary, but didn't really make any other connections to other parts of the gospel. The models are very good at summarizing existing information. I liked that 5.2 tried to make connections to other things. 