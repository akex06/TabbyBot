#   IMPORTS

import discord
import sqlite3 as sqlite
import tabby
import datetime

from tabby import Tabby
from discord.ext import commands

#   DATABASE
conn = sqlite.connect("./files/tabby.db")
c = conn.cursor()

# GET_PREFIX

async def get_prefix(client, message):
    result = await Tabby.get_prefix(message.guild)
    
    await Tabby.get_lang(message.guild)

    if not result:
        c.execute("INSERT INTO prefixes VALUES (?, ?)", (message.guild.id, "-"))
        conn.commit()
        return "-"
    
    return result[0]


#   VARIABLES

client = commands.Bot(command_prefix = get_prefix, intents = discord.Intents.all())

#   EVENTS

#   ON_READY
@client.event
async def on_ready():
    print(f"[ READY ]: {client.user}")
    print(f"[ INFO ]: The bot is in {len(client.guilds)}")
    print(f"[ INFO ]: The bot tracks {len(client.users)} users")

    await client.load_extension("cogs.settings")
    await client.load_extension("cogs.information")
    await client.load_extension("cogs.levels")
    await client.load_extension("cogs.economy")
    await client.load_extension("cogs.music")

#   ON_GUILD_JOIN
@client.event
async def on_guild_join(guild):
    result = c.execute("SELECT prefix FROM prefixes WHERE guild = ?", (guild.id, ))
    if not result:
        c.execute("INSERT INTO prefixes VALUES (?, ?)", (guild.id, "-"))
        conn.commit()

    print(f"[ GUILD+ ]: NAME: {guild.name}, MEMBERS: {len(guild.members)}")
    
#   ON_GUILD_LEAVE
@client.event
async def on_guild_leave(guild):
    print(f"[ GUILD- ]: NAME: {guild.name}, MEMBERS: {len(guild.members)}")

#   ON_MESSAGE
@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send((await Tabby.get_message(message.guild, "tabby.message.mentioned")).replace("{prefix}", await Tabby.get_prefix(message.guild)))

    await client.process_commands(message)

#   ON_COMMAND_ERROR
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send((await Tabby.get_message(ctx.guild, "commands.error.cooldown")).replace("{time}", str(datetime.timedelta(seconds = int(error.retry_after)))))

#   RUN
if __name__ == "__main__":
    client.run("ODY4NDcwMTkwNDk5ODI3NzYy.YPwH5A.7-VYv1nKFKw_iS4YXtdJfUpOmsQ")