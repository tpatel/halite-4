from kaggle_environments import evaluate, make
from IPython.display import display_html
import time

ts = time.time()

env = make("halite", debug=True)

env.run(["submission.py", "random", "random", "random"])

print(str(time.time() - ts))

html = env.render(mode="html")
json = env.render(mode="json")

with open("latest.html", "w") as f:
    f.write(html)

with open("replays/"+str(int(ts))+".json", "w") as f:
    f.write(json)
