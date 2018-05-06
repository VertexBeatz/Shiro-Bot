import discord
from discord.ext import commands as cmds
from core import Config


class Example518:
    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self.__class__.__name__, 23894723987423987)

        self.conf.register_global(is_ready=False)
        self.conf.register_guild(is_server_enabled=False)
        self.conf.register_channel(is_channel_enabled=False)
        self.conf.register_role(is_role_enabled=False)
        self.conf.register_member(is_member_enabled=False)
        self.conf.register_user(is_user_enabled=False)

    @cmds.command()
    async def botready(self, ctx: cmds.Context):
        txt = "is" if self.conf.is_ready() else "is not"
        await ctx.send("Bot {} ready.".format(txt))

    @cmds.command(pass_context=True)
    async def serverenablecheck(self, ctx: cmds.Context, set: bool=None):
        if set is not None:
            self.conf.server(ctx.guild).set("is_server_enabled", set)
        txt = "is" if self.conf.guild(ctx.guild).is_server_enabled \
            else "is not"
        await ctx.send("Bot {} server enabled.".format(txt))

    @cmds.command(pass_context=True)
    async def channelenablecheck(self, ctx: cmds.Context, set: bool=None):
        if set is not None:
            self.conf.channel(ctx.channel).set(
                "is_channel_enabled", set)
        txt = "is" if self.conf.channel(
            ctx.channel).is_channel_enabled() \
            else "is not"
        await ctx.send("Bot {} channel enabled.".format(txt))

    @cmds.command(pass_context=True)
    async def roleenablecheck(self, ctx: cmds.Context, role: discord.Role, set: bool=None):
        if set is not None:
            self.conf.role(role).set(
                "is_role_enabled", set)
        txt = "is" if self.conf.role(
            role).is_role_enabled() \
            else "is not"
        await ctx.send("Bot {} role enabled.".format(txt))

    @cmds.command(pass_context=True)
    async def memberenablecheck(self, ctx: cmds.Context, member: discord.Member,
                                set: bool=None):
        if set is not None:
            self.conf.member(member).set(
                "is_member_enabled", set)
        txt = "is" if self.conf.member(
            member).is_member_enabled() \
            else "is not"
        await ctx.send("Bot {} member enabled.".format(txt))

    @cmds.command(pass_context=True)
    async def userenablecheck(self, ctx: cmds.Context, user: discord.Member, set: bool=None):
        if set is not None:
            self.conf.user(user).set(
                "is_user_enabled", set)
        txt = "is" if self.conf.user(
            user).is_user_enabled() \
            else "is not"
        await ctx.send("Bot {} user enabled.".format(txt))

    async def on_ready(self):
        self.conf.set("is_ready", True)
