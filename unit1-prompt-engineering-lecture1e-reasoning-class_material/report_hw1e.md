## Parts 1 & 2
For these exercises, I asked the same questions to two agents, one with reasoning enabled, and one without reasoning enabled.

I first asked about stacking. The reasoning model got on my case about not stacking eggs, and wouldn't include them, but the non-reasoning just stacked them. 

I next asked about a recipe. Both models produced almost exactly the same output. The reasoning model didn't use very many reasoning tokens, but it did use some. Those tokens didn't help very much because the non-reasoning did fine.

I next asked about a word puzzle. I noticed that while the non-reasoning model didn't produce reasoning tokens, it seemed to reason as output. It would make a guess, and then correct itself. The reasoning model produced an incorrect but reasonable answer, but didn't seem to be able to apply one of the key clues from the puzzle, and neither could the other model, although it guessed right the first ime.

I next asked about a numeric puzzle. Both models got it right. For this type of question, it really wasn't worth it to use the reasoning, because the non-reasoning did fine.

I lastly asked about a random substitution cipher. Both models really struggled with it. The reasoning model I thought felt more sub-concious, where it really didn't want to give a wrong answer or make bad assumptions. I ended up having to help it a lot to get to an answer, which led it into context drift, so it took a long time. The non-reasoning model tried some options to reason through it as output, but eventually found an option and then incorrectly applied what it already knew about the cipher, which led it to produce the wrong answer.

Overall, it seemed like turning on the reasoning led to about twice the cost, which was especially not helpful for tasks that the non-reasoning model performed just fine. I especially liked being able to read the reasoning from the non-reasoning model, I thought it was useful. It didn't take too much longer for most questions, because the non-reasoning model outputted so much reasoning as just plain output. 

## Part 3

One thing I thought was really interesting about the constitution was how they arranged it to help 'teach' Claude good behaviour and ethics. They were hoping to make it so that it wasn't just a set of rules, but that the model would internalize the lessons to better apply the information. I was also suprised because they talked quite a lot about moral questions of who or what is Claude? They included a lot of notes about sense of identity, mental stability, having values, and expressing emotions. It's really interesting to see the way Anthropic thinks about their AI agent. We always say "well, it's not real", but it makes me wonder just exactly how real and mentally present the model is.