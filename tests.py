# import sqlite3 as sqlite
# import json

# with open("./files/langs.json", "r") as f:
#     data = json.load(f)

# conn = sqlite.connect("./files/tabby.db")
# c = conn.cursor()

# c.execute("CREATE TABLE economy (member INTEGER, guild INTEGER, bank INTEGER, wallet INTEGER)")
# conn.commit()

import os

path = f"{os.getcwd()}/guilds/"

l = [str(x) for x in range(10)]

for i in range(len(l)):
    new_path = f"{path}{i}"
    os.mkdir(new_path)