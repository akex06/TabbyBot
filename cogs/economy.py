#   IMPORTS
import discord
import tabby
import sqlite3 as sqlite
import random

from discord.ext import commands
from tabby import Tabby
from random import randint

#   DATABASE
conn = sqlite.connect("./files/tabby.db")
c = conn.cursor()

#   CLASS
class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    #   BALANCE COMMAND
    @commands.command(aliases = ["bal", "coins"])
    async def balance(self, ctx, member : discord.Member = None):
        #   IF MEMBER NONE MEMEBR WHO EXECUTED CONVERTS TO MEMBER
        if member == None:
            member = ctx.author

        #   GET ECONOMY BALANCE FROM MEMBER
        bank, wallet = await Tabby.get_bal(member)
        #   CREATE EMBED
        embed = discord.Embed(title = (await Tabby.get_message(ctx.guild, "balance.embed.title")).replace("{member.name}", member.name), description = (await Tabby.get_message(ctx.guild, "balance.embed.description")).replace("{member.name}", f"{member}").replace("{total}", str(bank + wallet)), color = Tabby.hexcolor)

        embed.add_field(name = await Tabby.get_message(ctx.guild, "balance.embed.bank"), value = bank)
        embed.add_field(name = await Tabby.get_message(ctx.guild, "balance.embed.wallet"), value = wallet)
        embed.set_footer(icon_url = self.client.user.avatar.url, text = await Tabby.get_message(ctx.guild, "tabby.invite.message"))
        #   SEND EMBED
        await ctx.send(embed = embed)
    
    #   PAY COMMAND
    @commands.command()
    async def pay(self, ctx, member : discord.Member = None, payed = 0):
        #   IF MEMBER NONE SEND ERROR
        if member == None:
            await ctx.send(await Tabby.get_message(ctx.guild, "economy.command.pay.error.none"))
            return
        #   IF MEMBER SAME AS EXECUTOR SEND ERROR
        if member == ctx.author:
            await ctx.send(await Tabby.get_message(ctx.guild, "economy.command.pay.error.self"))
            return
        #   IF PAYED AMOUNT IS LESS THAN 0 SEND ERROR
        if payed <= 0:
            await ctx.send(await Tabby.get_message(ctx.guild, "economy.command.pay.error.payed.none"))
            return

        #   GET AUTHOR AND RECEIVER BANK DETAILS
        author_bank, author_wallet = await Tabby.get_bal(ctx.author)
        bank, wallet = await Tabby.get_bal(member)
        
        #   IF AUTHOR BANK AMOUNT IS LESS THAN PAYED AMOUNT SEND ERROR
        if author_bank < payed:
            await ctx.send((await Tabby.get_message(ctx.guild, "economy.command.pay.error.payed.left")).replace("{left}", str(payed - author_bank)))
            return
        #   UPDATE BANK VALUES FOR EXECUTOR AND MEMBER
        c.execute("UPDATE economy SET bank = bank - ? WHERE member = ? AND guild = ?", (payed, ctx.author.id, ctx.author.guild.id))
        c.execute("UPDATE economy SET bank = bank + ? WHERE member = ? AND guild = ?", (payed, member.id, member.guild.id))
        conn.commit()
        #   CREATE EMBED
        embed = discord.Embed(description = (await Tabby.get_message(ctx.guild, "economy.command.pay.embed.description")).replace("{member.name}", str(ctx.author)).replace("{payed}", str(payed)).replace("{receiver.name}", str(member)), color = Tabby.hexcolor)
        embed.set_footer(icon_url = self.client.user.avatar.url, text = await Tabby.get_message(ctx.guild, "tabby.invite.message"))
        #   SEND EMBED
        await ctx.send(embed = embed)
    #   DEPOSIT COMMAND
    @commands.command(aliases = ["dep"])
    async def deposit(self, ctx, amount = 0):
        #   GET BANK DETAILS FROM CTX.AUTHOR
        bank, wallet = await Tabby.get_bal(ctx.author)
        #   IF AMOUNT OF MONEY TO DEPOSIT IS BIGGER THAN ACTUAL WALLET MONEY SEND ERROR
        if amount > wallet:
            await ctx.send((await Tabby.get_message(ctx.guild, "economy.command.deposit.notenough")).replace("{left}", str(amount - wallet)))
            return
        #   UPDATE BANK DETAILS FOR CTX.AUTHOR
        c.execute("UPDATE economy SET wallet = wallet - ?, bank = bank + ? WHERE member = ? AND guild = ?", (amount, amount, ctx.author.id, ctx.author.guild.id))
        conn.commit()
        #   CREATE EMBED
        embed = discord.Embed(description = (await Tabby.get_message(ctx.guild, "economy.command.deposit.embed.description")).replace("{amount}", str(amount)), color = Tabby.hexcolor)
        embed.set_footer(icon_url = self.client.user.avatar.url, text = await Tabby.get_message(ctx.guild, "tabby.invite.message"))
        #   SEND EMBED
        await ctx.send(embed = embed)
    #   WITHDRAW COMMAND
    @commands.command(aliases = ["w"])
    async def withdraw(self, ctx, amount = 0):
        #   GET BANK DETAILS FROM CTX.AUTHOR
        bank, wallet = await Tabby.get_bal(ctx.author)
        #   IF AMOUNT OF MONEY TO WITHDRAW IS BIGGER THAN ACTUAL BANK AMOUNT SEND ERROR
        if amount > bank:
            await ctx.send((await Tabby.get_message(ctx.guild, "economy.command.withdraw.notenough")).replace("{left}", str(amount - wallet)))
            return
        #   UPDATE BANK DETAILS FOR CTX.AUTHOR
        c.execute("UPDATE economy SET wallet = wallet + ?, bank = bank - ? WHERE member = ? AND guild = ?", (amount, amount, ctx.author.id, ctx.author.guild.id))
        conn.commit()
        #   CREATE EMBED
        embed = discord.Embed(description = (await Tabby.get_message(ctx.guild, "economy.command.withdraw.embed.description")).replace("{amount}", str(amount)), color = Tabby.hexcolor)
        embed.set_footer(icon_url = self.client.user.avatar.url, text = await Tabby.get_message(ctx.guild, "tabby.invite.message"))
        #   SEND EMBED
        await ctx.send(embed = embed)
    #   ADDMONEY EMBED (ADMINISTRATOR)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def addmoney(self, ctx, member : discord.Member = None, amount = 0):
        #   IF MEMBER IS NONE THEN CTX.AUTHOR CONVERTS TO MEMBER
        if member == None:
            member = ctx.author
        #   UPDATE BANK DETAILS OF MEMBER
        c.execute("UPDATE economy SET bank = bank + ? WHERE member = ? AND guild = ?", (amount, member.id, member.guild.id))
        conn.commit()
        #   SEND MESSAGE OF SUCCESS
        await ctx.send((await Tabby.get_message(ctx.guild, "economy.command.addmoney.success")).replace("{amount}", str(amount)).replace("{member.name}", str(member)))
    #   DAILY COMMAND
    @commands.command()
    #   EVERY ONCE IN 86400 SECONDS (24 HOURS) THIS COMMAND CAN BE EXECUTED
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        #   CHECK IF CTX.AUTHOR HAS A BANK ACCOUNT
        await Tabby.get_bal(ctx.author)
        #   GET AMOUNT FOR DAILY
        amount = random.randint(100, 150)
        #   UPDATE CTX.AUTHOR BANK DETAILS
        c.execute("UPDATE economy SET bank = bank + ? WHERE member = ? AND guild = ?", (amount, ctx.author.id, ctx.author.guild.id))
        conn.commit()
        #   SEND SUCCESS MESSAGE
        await ctx.send((await Tabby.get_message(ctx.guild, "economy.commands.daily.success")).replace("{amount}", str(amount)))
    #   REMOVEMONEY COMMAND
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def removemoney(self, ctx, member : discord.Member = None, amount = 0):
        #   IF MEMBER IS NONE THEN CTX.AUTHOR CONVERTS TO MEMBER
        if member == None:
            member = ctx.author
        #   UPDATE BANK DETAILS FOR MEMBER
        c.execute("UPDATE economy SET bank = bank - ? WHERE member = ? AND guild = ?", (amount, member.id, member.guild.id))
        conn.commit()
        #   SEND SUCCESS MESSAGE
        await ctx.send((await Tabby.get_message(ctx.guild, "economy.command.removemoney.success")).replace("{amount}", str(amount)).replace("{member.name}", str(member)))

async def setup(client):
    await client.add_cog(Economy(client))