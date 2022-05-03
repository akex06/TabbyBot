#   IMPORTS
import json
import os
import os.path
import sqlite3 as sqlite
import random

from os import path
from random import randint

#   DATABASE
conn = sqlite.connect("./files/tabby.db")
c = conn.cursor()

#   LOADING langs.json FILE
with open("./files/langs.json", "r") as f:
    data = json.load(f)

#   TABBY CLASS
class Tabby:
    #   HEX COLOR FOR EMBEDS
    hexcolor = 0xffd119

    #   GET PREFIX
    async def get_prefix(guild):
        if guild == None:
            return "-"
        #   GET PREFIX FROM DB
        result = c.execute("SELECT prefix FROM prefixes WHERE guild = ?", (guild.id, )).fetchone()
        #   IF PREFIX IS NOT FOUND
        if not result:
            #   INSERT INTO TABLE
            c.execute("INSERT INTO prefixes VALUES (?, ?)", (guild.id, "-"))
            conn.commit()

            #   RETURN DEFAULT PREFIX
            return "-"

        #   RETURN EXISTING PREFIX
        return result[0]

    # GET GUILD LANG
    async def get_lang(guild):
        #   GET LANG FROM DB
        lang = c.execute("SELECT lang FROM langs WHERE guild = ?", (guild.id, )).fetchone()
        #   IF LANG IS NOT FOUND
        if not lang:
            #   INSERT INTO TABLE
            c.execute("INSERT INTO langs VALUES (?, ?)", (guild.id, data["SETTINGS"]["default-lang"]))
            conn.commit()

            #   RETURN DEFAULT LANG
            return data["SETTINGS"]["default-lang"]
            
        return lang[0]
    
    #   GET LEVEL FROM DB
    async def get_level(member):
        #   GET LEVEL DATA
        result = c.execute("SELECT level, exp FROM levels WHERE member = ? AND guild = ?", (member.id, member.guild.id)).fetchone()
        #   IF DATA IS NONE
        if not result:
            c.execute("INSERT INTO levels VALUES (?, ?, ?, ?)", (member.guild.id, member.id, 1, 0))
            conn.commit()
            #   ADD EXP TO MEMBER
            await Tabby.add_exp(member)
            #   GET LEVEL AND EXP FROM DATABASE
            result = c.execute("SELECT level, exp FROM levels WHERE member = ? AND guild = ?", (member.id, member.guild.id)).fetchone()
            #   RETURN VALUES FROM RESULT
            return result
        
        #   IF DATA EXISTS
        return result        

    #   ADD EXP AND ADD LEVEL IF NEEDED
    async def add_exp(member):
        #   GET LEVEL AND EXP FROM MEMBER
        level, exp = await Tabby.get_level(member)
        next_level = level + 1
        #   ADD EXP TO MEMBER
        exp += random.randint(5, 20)
        #   GET EXP_NEEDED FOR LEVELUP
        exp_needed = level * (175 * level) * 0.5
        #   IF EXP IS BIGGER THAN EXP_NEEDED
        if exp >= exp_needed:
            #   UPDATE LEVEL DETAILS FOR MEMBER
            c.execute("UPDATE levels SET level = level + 1, exp = ? WHERE member = ? AND guild = ?", (exp, member.id, member.guild.id))
            conn.commit()
            #   RETURN LEVEL AND EXP FROM MEMBER
            return (level, exp)
        #   UPDATE LEVEL DETAILS FOR MEMBER
        c.execute("UPDATE levels SET exp = ? WHERE member = ? AND guild = ?", (exp, member.id, member.guild.id))
        conn.commit()
        #   RETURN LEVEL AND EXP FOR MEMBER
        return (level - 1, exp)
        
    #   GET MESSAGE FROM langs.json FILE
    async def get_message(guild, message):
        #   GET LANGUAGE FROM SERVER
        lang = await Tabby.get_lang(guild)
        #   GET MESSAGE FROM langs.json
        _message = data[lang][message]
        #   RETURN _message
        return _message

    #   GET BALANCE
    async def get_bal(member):
        #   GET BALANCE DETAILS FROM MEMBER
        result = c.execute("SELECT bank, wallet FROM economy WHERE member = ? AND guild = ?", (member.id,  member.guild.id)).fetchone()
        #   IF RESULT DOESN'T EXIST
        if not result:
            #   INSERT VALUES FOR MEMBER DETAILS
            c.execute("INSERT INTO economy VALUES (?, ?, ?, ?)", (member.id, member.guild.id, 0, 100))
            conn.commit()

            return (0, 100)
        #   RETURN IF RESULT EXISTS
        return result

    #   ADD BAL
    async def add_bal(member, bank = 0, wallet = 0):
        #   CHECK MEMBER HAS AN ACCOUNT
        await Tabby.get_bal(member)
        #   UPDATE ECONOMY DETAILS FOR MEMBER
        c.execute("UPDATE economy SET bank = bank + ?, wallet = wallet + ? WHERE member = ? AND guild = ?", (bank, wallet, member.id, member.guild.id))
        conn.commit()
        #   RETURN BALANCE DETAILS FOR MEMBER
        return await Tabby.get_bal(member)