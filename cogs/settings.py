#   IMPORTS
import discord
import sqlite3 as sqlite
import json

from discord.ext import commands
from tabby import Tabby

#   DATABASE
conn = sqlite.connect("./files/tabby.db")
c = conn.cursor()

#   LANGUAGE FILE
with open("./files/langs.json", "r") as f:
    data = json.load(f)

#   COG CLASS
class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    #   SET PREFIX
    @commands.command(aliases = ["changeprefix"])
    @commands.has_permissions(administrator = True)
    async def setprefix(self, ctx, prefix = None):
        #   PREFIX NOT DEFINED
        if prefix == None:
            await ctx.send(Tabby.get_message(ctx.guild, "setprefix.error.none"))
            return

        #   UPDATE PREFIX
        c.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?", (prefix, ctx.guild.id))
        conn.commit()

        await ctx.send((await Tabby.get_message(ctx.guild, "setprefix.message.success")).replace("{prefix}", prefix))

    #   SET LANGUAGE
    @commands.command(aliases = ["changelang", "setlanguage", "changelanguage"])
    @commands.has_permissions(administrator = True)
    async def setlang(self, ctx, lang = None):
        #   IF LANG HAS NOT BEEN DEFINED SEND ERROR
        if lang == None:
            await ctx.send(await Tabby.get_message(ctx.guild, "setlang.error.none"))
            return
        #   IF LANG IS NOT IN AVAILABLE LANGS INSIDE langs.json SEND ERROR
        if not lang.upper() in data["SETTINGS"]["available-langs"]:
            await ctx.send(await Tabby.get_message(ctx.guild, "setlang.error.langnotfound"))
            return
        #   UPDATE SERVER LANG
        c.execute("UPDATE langs SET lang = ? WHERE guild = ?", (lang, ctx.guild.id))
        conn.commit()
        #   SEND SUCCESS MESSAGE
        await ctx.send((await Tabby.get_message(ctx.guild, "setlang.message.success")).replace("{lang}", lang))
        
        

#   ADD COG
async def setup(client):
    await client.add_cog(Settings(client))