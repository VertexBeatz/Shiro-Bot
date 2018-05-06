import discord
from discord.ext import commands

from __main__ import send_cmd_help
from cogs.utils import checks

import datetime
import asyncio

from .utils.dataIO import dataIO, fileIO
import os

class france:
    """None"""

    def __init__(self, bot):
        self.bot = bot
        self.welcome = "data/france/settings.json"
        self.path = dataIO.load_json(self.welcome)
    
    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def fw(self,ctx, channel: discord.Channel,*, content:str):
        
        await self.bot.delete_message(ctx.message)
        try:
            await self.bot.send_message(channel, content)
        except:
            await self.bot.say("Pas accès au channel")

    @commands.group(pass_context=True, no_pm=True, aliases=["suppr"],name="del")
    @checks.mod_or_permissions(manage_messages=True)
    async def supprdel(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
    
    @supprdel.command(pass_context=True)
    async def user(self, ctx,number:int, *, user: discord.Member=None):
        """Delete x messages of a user"""

        if not user:
            await self.bot.say("Who?")
            return
        if not number:
            await self.bot.say("Number?")
            return

        m = ctx.message
        a = 0

        try:
            async for message in self.bot.logs_from(m.channel, limit=100):
                if message.author == user:
                    try:
                        await self.bot.delete_message(message)
                        await asyncio.sleep(0.6)
                        a += 1
                        if a == number:
                            return
                    except:
                        pass
        except:
            await self.bot.say("I don't have perms to add roles.")

    @supprdel.command(pass_context=True)
    async def date(self,ctx, content:str):
        """Still in development
        
        Delete all messages before the date wrote"""
        m = ctx.message

        if not content:
            await self.bot.say("Like this `Year-Month-Day`")
        
        try:
            a = datetime.datetime.strptime(content, '%Y-%m-%d')
        except:
            await self.bot.say("Erreur time")
            return
        nb = 0
        try:
            async for message in self.bot.logs_from(m.channel, limit=100000):
                await asyncio.sleep(0.1)
                if message.channel.id == m.channel.id:
                    if message.timestamp < a:
                        try:
                            await self.bot.delete_message(message)
                            await asyncio.sleep(0.6)
                            nb += 1
                        except:
                            pass
        except:
            await self.bot.say("error")
            pass
        await self.bot.send_message(m.author, "Done, {}".format(nb))

    @supprdel.command(pass_context=True)
    async def number(self,ctx, context:int):
        """Number of messages to delete"""
        m = ctx.message

        if not context:
            await self.bot.say("Number of messages?")

        try:
            async for message in self.bot.logs_from(m.channel, limit=context):
                try:
                    await self.bot.delete_message(message)
                    await asyncio.sleep(0.6)
                except:
                    pass
        except:
            await self.bot.say("I don't have perms to del messages.")

    async def on_message(self,message):
        if message.server.id == "283534045655334912":
            if message.channel.id == "283591572686241793":
                if message.author == self.bot.user:
                    return
                try:
                    ancien = message
                    await self.bot.delete_message(message)
                    await self.bot.send_message(message.author, "Demande de fiches bien envoyée aux administrateurs !")
                    serv = self.bot.get_all_channels()
                    channels = [c for c in serv
                                if c.id == "434470258611585024"]
                    channel = channels[0]
                    msg = "Message de: Nom: {} ID: {}\n{}".format(ancien.author.name, ancien.author.id,ancien.content)
                    await self.bot.send_message(channel,msg)
                except:
                    print(message.context)
def check_folder():
    if not os.path.exists('data/france'):
        os.mkdir('data/france')


def check_files():
    f = 'data/france/settings.json'
    if not os.path.exists(f):
        fileIO(f, 'save', {})


def setup(bot):
    check_folder()
    check_files()
    n = france(bot)
    bot.add_cog(n)