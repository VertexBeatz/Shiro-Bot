import discord
from discord.ext import commands

from __main__ import send_cmd_help
from cogs.utils import checks

from .utils.dataIO import dataIO

class Role:
    """Be able to allow users to gain roles"""

    def __init__(self, bot):
        self.bot = bot
        self.role_path = "data/role/role.json"
        self.path = dataIO.load_json(self.role_path)


    @commands.group(pass_context=True)
    @checks.admin()
    async def publicrole(self, ctx):
        """Adds / removes roles to the public role list"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)    

    @publicrole.command(pass_context=True, no_pm=True, name="add")
    async def _add(self,ctx, *, role: discord.Role):
        """Add a role to the public role list"""

        message = ctx.message
        server = message.server
        
        if server.id not in self.path["guilds"]:
            self.path["guilds"][server.id] = {}

        self.path["guilds"][server.id][role.name] = role.id
        dataIO.save_json(self.role_path, self.path)
        await self.bot.say("Done!")
    
    @publicrole.command(pass_context=True, no_pm=True, name="remove")
    async def _remove(self, ctx, role: discord.Role):
        """Remove a role from the public role list"""

        message = ctx.message
        server = message.server

        del self.path["guilds"][server.id][role.name]
        dataIO.save_json(self.role_path, self.path)
        await self.bot.say("Done!")

    @commands.group(pass_context=True)
    async def role(self,ctx):
        """Info about the public role list"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx) 

    @commands.command(pass_context=True, no_pm=True)
    async def serverlist(self,ctx):
        """List all the roles on the server"""

        message = ctx.message
        server = message.server
        start = ""
        nb = 0

        em = discord.Embed(title="All the roles in the guild")
        for x in server.roles:
            c= x.name+ " , "+x.mention+" , "+x.id+"\n"
            start += c
            if len(start) > 1000:
                if nb == 0:
                    em.description=start
                    nb = 1
                else:
                    em.description = start
                await self.bot.say(embed=em)
                start = ""
                em = discord.Embed(title="\u200b")
        if len(start)>5:
            em.description = start
            await self.bot.say(embed=em)

    @role.command(pass_context=True, no_pm=True, name="list")
    async def _list(self,ctx):
        """Show the public role list"""
        message = ctx.message
        server = message.server

        start = ""
        em = discord.Embed(title="Guild role list")
        nb = 0


        for i in range(len(self.path["guilds"][server.id])):
            a = list(self.path["guilds"][server.id])[i]
            b = discord.utils.get(server.roles, id=self.path["guilds"][server.id][a])
            if not b:
                pass
            else:
                c = b.name +" , "+b.mention +"\n"
                start += c
                if len(start) > 1000:
                    if nb == 0:
                        em.description = start
                        nb = 1
                    else:
                        em.description = start                 
                    await self.bot.say(embed=em)
                    start = ""   
                    em = discord.Embed(title="\u200b")
        if len(start) >5:
            em.description = start
            await self.bot.say(embed=em)

    @role.command(pass_context=True, no_pm=True, name="get")
    async def _get(self,ctx,*,rolename):
        """Get a role from the publicrole list
        
        If you already have It, take It back"""
        
        message = ctx.message
        server = message.server

        if rolename not in self.path["guilds"][server.id]:
            await self.bot.say("This role doesn't exist or isn't in the list, be sure to spell It correctly ^^")
        else:
            for role in message.author.roles:
                if role.name == rolename:
                    try:
                        role = discord.utils.get(server.roles, id=self.path["guilds"][server.id][rolename])
                        await self.bot.remove_roles(message.author, role)
                        await self.bot.say("{}, You lost the role: {}".format(message.author.mention, role.name))
                    except:
                        await self.bot.say("There is an error")
                    return

                if "Color" in role.name and "Color" in rolename:
                    try:
                        await self.bot.remove_roles(message.author, role)
                        await self.bot.say("{}, You lost the role: {}".format(message.author.mention, role.name))
                    except:
                        await self.bot.say("There is an error")
            try:
                role = discord.utils.get(server.roles, id=self.path["guilds"][server.id][rolename])
                await self.bot.add_roles(message.author, role)
                await self.bot.say("{}, You now have the role: {}".format(message.author.mention, role.name))
            except:
                await self.bot.say("There is an error")






def setup(bot):
    bot.add_cog(Role(bot))