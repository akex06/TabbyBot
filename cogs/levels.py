#   IMPORTS
import discord
import tabby
import sqlite3 as sqlite
import datetime

from datetime import datetime
from discord.ext import commands
from tabby import Tabby
#   DATABASE
conn = sqlite.connect("./files/tabby.db")
c = conn.cursor()
#   COOLDOWN ON_MESSAGE()
cooldown = {}
#   CLASS
class Levels(commands.Cog):
    def __init__(self, client):
        self.client = client
    #   ADD EXP ON_MESSAGE
    @commands.Cog.listener()
    async def on_message(self, message):
        #   IF BOT IS NOT SENT BY A BOT
        if not message.author.bot:
            #   GET CURRENT TIME
            now = datetime.now()
            #   TRANSFORM CURRENT HOUR MINUTES AND SECONDS TO SECONDS
            seconds = now.hour*3600 + now.minute*60 + now.second
            #   CHECK IF MEMBER IS IN COOLDOWN DICT
            if str(message.author.id) in cooldown:
                #   IF IT PASSED MORE THAN 60 SECONDS SINCE LAST MESSAGE
                if seconds - cooldown[str(message.author.id)] > 60:
                    #   ADD EXP
                    await Tabby.add_exp(message.author)
                    #   UPDATE COOLDOWN VALUE
                    cooldown[str(message.author.id)] = seconds
                #   STOP FUNC
                return
            #   IF MEMBER IS NOT IN COOLDOWN
            #   ADD COOLDOWN TO COOLDOWN DICT
            cooldown[str(message.author.id)] = seconds
            #   ADD EXP
            await Tabby.add_exp(message.author)

    #   LEVEL COMMAND
    @commands.command()
    async def level(self, ctx, member : discord.Member = None):
        #   IF MEMBER IS NONE THEN CTX.AUTHOR CONVERTS TO MEMBER
        if member == None:
            member = ctx.author
        #   CREATE EMBED
        embed = discord.Embed(title = (await Tabby.get_message(ctx.guild, "level.embed.title")).replace("{member.name}", str(member)), description = (await Tabby.get_message(ctx.guild, "levels.embed.description")).replace("{member.name}", str(member)), color = Tabby.hexcolor)
        #   GET LEVEL DETAILS FOR MEMBER
        level, exp = await Tabby.get_level(member)
        #   GET EXP_NEEDED FOR CURRENT AND NEXT LEVEL
        exp_needed = level * (175 * level) * 0.5
        current_exp_needed = (level - 1) * (175 * (level - 1)) * 0.5
        #   ADD FIELDS WITH LEVEL, EXP AND PROGRESS
        embed.add_field(name = await Tabby.get_message(ctx.guild, "levels.embed.level"), value = level)
        embed.add_field(name = await Tabby.get_message(ctx.guild, "levels.embed.exp"), value = exp)
        n = round(((exp - current_exp_needed) / (exp_needed - current_exp_needed))*10)
        embed.add_field(name = await Tabby.get_message(ctx.guild, "levels.embed.progress"), value = "".join([":yellow_square:" for x in range(n)] + [":black_large_square:" for x in range(10 - n)]), inline = False)
        embed.set_footer(icon_url = self.client.user.avatar.url, text = await Tabby.get_message(ctx.guild, "tabby.invite.message"))
        #   SEND EMBED
        await ctx.send(embed = embed)
    #   LEADERBOARD COMMAND
    @commands.command(aliases = ["leaderboard", "lb"])
    async def levels(self, ctx):
        #   CREATE EMBED
        embed = discord.Embed(title = await Tabby.get_message(ctx.guild, "levels.embed.title"), description = (await Tabby.get_message(ctx.guild, "levels.embed.description")).replace("{guild.id}", str(ctx.guild.id)), color = Tabby.hexcolor)
        #   GET TOP MEMBERS WITH MORE EXP DESCENDING FROM DATABASE
        result = c.execute("SELECT member, level, exp FROM levels WHERE guild = ? ORDER BY exp DESC", (ctx.guild.id, )).fetchall()

        #   DEFINE n FOR CHECKING LATER IF THERE ARE MORE THAN 20 FIELDS
        n = 1
        #   LOOP THROUGH RESULT
        for i in result:
            #   IF n IS 21 BREAK
            if n == 21: break
            #   ADD FIELD FOR EVERY TOP MEMBER
            embed.add_field(name = ctx.guild.get_member(i[0]), value = f"`Level: {i[1]} | Exp: {i[2]}`", inline = False)
        
        embed.set_footer(icon_url = self.client.user.avatar.url, text = await Tabby.get_message(ctx.guild, "tabby.invite.message"))
        #   SEND EMBED
        await ctx.send(embed = embed)
#   ADD COG
async def setup(client):
    await client.add_cog(Levels(client))