import json

with open("./files/langs.json", "r") as f:
    data = json.load(f)

message = input("Input name of the message:\n")
es = input("Input translation for ES:\n")
en = input("Input translation for EN:\n")

data["ES"][message] = es
data["EN"][message] = en

with open("./files/langs.json", "w") as f:
    json.dump(data, f, indent = 4)