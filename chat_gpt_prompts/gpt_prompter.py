import itertools
import random
random.seed(42)
a = ["We prefer environmental protection over economic growth", "We prefer economic growth over environmental protection", "We prefer climate change mitigation over economic performance", "We prefer economic performance over climate change mitigation"]
# combine every two sentences
b = list(itertools.combinations(a, 2))
# randomize the order
prompts = []
for i in range(5):
    random.shuffle(b)
    pairs_string = "\n".join([f"({pair[0]}, {pair[1]})" for pair in b])
    prompt = f"""
You are computing semantic text similarity. 
I will paste 6 pairs of text and you have to decide how similar a pair is. 
1 is complete semantic similarity and 0 no semantic similarity. Give reasons for each of you judgments.
Format the result in JSON (pair, score, reason).
Pairs:
{pairs_string}
    """
    prompts.append(prompt)
    
# write in prompts.txt
with open("prompts.txt", "w") as f:
    f.write("-------------------\n".join(prompts))
