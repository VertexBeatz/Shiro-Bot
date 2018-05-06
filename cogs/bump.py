import discord
from discord.ext import commands
from cogs.utils import checks

class Bump:
    """Every bump commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def bump1(self,ctx):
        
        await self.bot.say("!disboard bump")

    @commands.command(pass_context=True, no_pm=True)
    async def bump2(self,ctx):
        
        await self.bot.say("=bump")

    @commands.command(pass_context=True, no_pm=True)
    async def bump3(self,ctx):
        
        await self.bot.say(";;bump")

    @commands.command(pass_context=True, no_pm=True)
    async def bump4(self,ctx):
        
        await self.bot.say("dlm!bump")

def setup(bot):
    bot.add_cog(Bump(bot))