#   IMPORTS
import os
import discord
import tabby
import sqlite3 as sqlite

from discord.ext import commands
from tabby import Tabby

#   DATABASE
conn = sqlite.connect("./files/tabby.db")
c = conn.cursor()

#   MUSIC CLASS
class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    #   PLAY COMMAND
    @commands.command(aliases = ["p"])
    async def play(self, ctx, music = None):
        if music == None:
            embed = discord.Embed(description = f"**Usage:** {(await Tabby.get_message(ctx.guild, 'play.command.error.usage')).replace('{prefix}', await Tabby.get_prefix(ctx.guild))}\n**Description:** {await Tabby.get_message(ctx.guild, 'play.command.error.description')}", color = Tabby.hexcolor)
            await ctx.send(embed = embed)
            return


#   ADD COG
async def setup(client):
    await client.add_cog(Music(client))