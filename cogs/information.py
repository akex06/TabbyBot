import discord
import tabby

from discord.ext import commands
from tabby import Tabby

class Information(commands.Cog):
    def __init__(self, client):
        self.client = client

    #   SERVER INFORMATION COMMAND
    @commands.command(aliases = ["information", "serverinfo", "serverinformation"])
    async def info(self, ctx):
        guild = ctx.guild

        #   CREATE EMBED
        embed = discord.Embed(title = await Tabby.get_message(ctx.guild, "server.information.title"), description = (await Tabby.get_message(guild, "server.information.description")).replace("{guild.name}", ctx.guild.name), color = Tabby.hexcolor)
        #   ADD FIELDS
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.owner"), value = guild.owner)
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.id"), value = guild.id)
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.members"), value = len(guild.members))
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.description"), value = guild.description)
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.language"), value = await Tabby.get_lang(guild))
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.created_at"), value = guild.created_at)
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.categories"), value = len(guild.categories))
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.channels"), value = len(guild.channels))
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.text_channels"), value = len(guild.text_channels))
        embed.add_field(name = await Tabby.get_message(guild, "server.fields.voice_channels"), value = len(guild.voice_channels))
        embed.set_image(url = guild.icon.url)
        embed.set_footer(icon_url = self.client.user.avatar.url, text = await Tabby.get_message(ctx.guild, "tabby.invite.message"))
        #   SEND EMBED
        await ctx.send(embed = embed)
    #   CHECK SERVER LANGUAGE (STUPID COMMAND BUT IT EXISTS)
    @commands.command()
    async def lang(self, ctx):
        lang = await Tabby.get_lang(ctx.guild)
        message = (await Tabby.get_message(ctx.guild, "commands.lang")).replace("{lang}", lang)

        await ctx.send(message)
    #   CHECK BOTS PREFIX (STUPID COMMAND BUT IT EXISTS)
    @commands.command()
    async def prefix(self, ctx):
        prefix = await Tabby.get_prefix(ctx.guild)

        await ctx.send((await Tabby.get_message(ctx.guild, "commands.prefix")).replace("{prefix}", prefix))

async def setup(client):
    await client.add_cog(Information(client))