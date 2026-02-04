## Homework 2a report

### Testing similar/dissimilar outputs

One discovery I found was that upper and lower case versions of the same word didn't produce the same embeddings.

I found that it mapped adjectives more closely to other adjectives than verbs or nouns of the same ideas. It ranked "happily" as more similar to "quickly" than to "run".

I used "Hello" as a base word for a lot of investigations.
I found that antonyms of words scored higher than random words. "Goodbye" was better than "chicken".
Minor typos usually scored higher than antonyms, though, words like "hillo" and "hllo", with narrow misses by "heplo" and "heklo". 
I found that even five-letter goobledegook scored better than "chicken". I tried a keyboard shift on hello, turning it into "gwkki", and it scored about as well on that as some of the lower-ranking typos. A Caeser cipher shift got about the same score as well. 
I was surprised to find that even a really long, gobbledegook text did better than "chicken", but a nonsense English sentence didn't.

One experiment I did was with the word "Tiana". It was rated fairly similarly to "Princess and the Frog", but not as much to the other characters in that movie.
I tried to compare Tiana to other princess names. I found that the ones that scored the highest were the princesses with uncommon names, and what seemed to be other five letter names. I found that the actress who voiced Tiana scored about as high as the rest of the princesses. However, none of them were particularly high. They all scored below .6, which was interesting. Another interesting pattern was that all the princesses were about as related to "Tiana" as they were to "Disney Princess". 

My next experiment was that I put in a bunch of Star Wars characters name, and cycled through comparing each of them to each of the others. For most of the characters, the embedding scores were almost identical, and most of them were about even. Some of the names it struggled with connections to were shorter or more generic names, like "Yoda","Finn", and "Grogu", and less well-known characters. I thought that it seemed like some of the classification wasn't based as much on the context of the word (like Star Wars sequel trilogy character), as much as it seemed to be comparing general structure. With some of the less-known characters, especially, it seemed to be more comparing the structure of the name, like how long it was, or what letter patterns were similar.

### Different languages

One thing I tried was embeddings for things similar to "1234". The Italian for "one two three four" was closer than most of the other unrelated inputs. However, the python code that prints "1234" scored lower than "happily". However, just changing "1234" to "1,2,3,4" caused the python code to be more similar, as well as the input "1 + 2 = 3". 

One thing I tried was comparing "hello" to other langauges. All of them scored lower than a common misspelling of "hllo", but most scored higher than "goodbye". It seemed to score European languages higher than Asian languages.


### Chunking size and its impact on lookup

I used the 1st Nephi text to lookup information on "build boat". The first way I chunked it was using lines, where my text split on each line in my text file. It seemed to do really well with this. All the lines were about boats, and even some more tangentially related like, which referenced the sea. I next split it up by sentence, and I got very similar results. I next tried chunk sizes of just 30 characters. I think this was too small, because I got a lot of matches that were only tangentially related. I got a lot of build, some of which were Nephi building the boat, but some were just words like "built", and I got a few that only had to do with sand, or sunk, or sea. I next tried with larger sections, with 500 characters each. I got fewer matches when doing that. The ones I did get was where it talked about boats or building for the entire section. I think this was a little too long, because it didn't include as much as the smaller chunks.