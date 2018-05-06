import os
import inspect
import discord
import asyncio
from .utils import checks
from datetime import datetime
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO


DB_VERSION = 2


# TODO
# Better error handling (dumping errors in terminal)
# Better errors returning to channels
# ignore entire channel in channel events

class Grenzpolizei:
    def __init__(self, bot):
        self.bot = bot

        self.settings_file = 'data/grenzpolizei/settings.json'
        self.settings = dataIO.load_json(self.settings_file)
        self.ignore_file = 'data/grenzpolizei/ignore.json'
        self.ignore = dataIO.load_json(self.ignore_file)

        self.event_types = {}

        self.event_types['on_member_join'] = 'member_event_channel'
        self.event_types['on_member_remove'] = 'member_event_channel'
        self.event_types['on_member_ban'] = 'member_event_channel'
        self.event_types['on_member_unban'] = 'member_event_channel'
        self.event_types['on_member_update'] = 'member_event_channel'
        self.event_types['on_voice_state_update'] = 'member_event_channel'

        self.event_types['on_message_edit'] = 'message_event_channel'
        self.event_types['on_message_delete'] = 'message_event_channel'

        self.event_types['on_channel_create'] = 'server_event_channel'
        self.event_types['on_channel_delete'] = 'server_event_channel'
        self.event_types['on_channel_update'] = 'server_event_channel'

        self.event_types['on_server_role_create'] = 'server_event_channel'
        self.event_types['on_server_role_delete'] = 'server_event_channel'
        self.event_types['on_server_role_update'] = 'server_event_channel'

        self.event_types['on_warning'] = 'mod_event_channel'
        self.event_types['on_kick'] = 'mod_event_channel'
        self.event_types['on_ban'] = 'mod_event_channel'

        self.green = discord.Color.green()
        self.orange = discord.Color.orange()
        self.red = discord.Color.red()
        self.blue = discord.Color.blue()

    async def _validate_server(self, server):
        return True if server.id in self.settings else False

    async def _validate_event(self, server):
        try:
            return self.settings[server.id]['events'][inspect.stack()[1][3]] if await self._validate_server(server) else False
        except KeyError:
            return False

    async def _get_channel(self, server):
        return discord.utils.get(self.bot.get_all_channels(), id=self.settings[server.id]['channels'][self.event_types[inspect.stack()[2][3]]])

    async def _send_message_to_channel(self, server, embed=None):
        channel = await self._get_channel(server)
        await self.bot.send_message(channel, embed=embed)

    async def _save_settings(self):
        dataIO.save_json(self.settings_file, self.settings)

    async def _yes_no(self, question, author):
        bot_message = await self.bot.say(question)
        message = await self.bot.wait_for_message(timeout=120, author=author)
        if message:
            if any(n in message.content.lower() for n in ['yes', 'y']):
                await self.bot.edit_message(bot_message, '**{} Yes**'.format(question))
                try:
                    await self.bot.delete_message(message)
                except:
                    pass
                return True
        await self.bot.edit_message(bot_message, '**{} No**'.format(question))
        try:
            await self.bot.delete_message(message)
        except:
            pass
        return False

    async def _what_channel(self, question, author):
        bot_message = await self.bot.say(question)
        message = await self.bot.wait_for_message(timeout=120, author=author)
        if message:
            channel = message.raw_channel_mentions[0]
            await self.bot.edit_message(bot_message, '**{}**'.format(question))
            if channel:
                return channel
            else:
                return False
        return False

    async def _ignore(self, server, member=None, channel=None):
        await self._ignore_server_check(server)
        if channel:
            if channel.id in self.ignore[server.id]['channels']:
                return False
        if member:
            if member.id in self.ignore[server.id]['members']:
                return False
        return True

    async def _ignore_save(self):
        dataIO.save_json(self.ignore_file, self.ignore)

    async def _ignore_server_check(self, server):
        if server.id not in self.ignore:
            self.ignore[server.id] = {}
            self.ignore[server.id]['members'] = {}
            self.ignore[server.id]['channels'] = {}
        return True

    async def ignoremember(self, server, member):
        await self._ignore_server_check(server)
        if member.id in self.ignore[server.id]['members']:
            del self.ignore[server.id]['members'][member.id]
            await self._ignore_save()
            return 'Tracking {} again'.format(member.mention)
        else:
            self.ignore[server.id]['members'][member.id] = True
            await self._ignore_save()
            return 'Not tracking {} anymore'.format(member.mention)

    async def ignorechannel(self, server, channel):
        await self._ignore_server_check(server)
        if channel.id in self.ignore[server.id]['channels']:
            del self.ignore[server.id]['channels'][channel.id]
            await self._ignore_save()
            return 'Tracking {} again'.format(channel.mention)
        else:
            self.ignore[server.id]['channels'][channel.id] = True
            await self._ignore_save()
            return 'Not tracking {} anymore'.format(channel.mention)

    async def _setup_questions(self, context):
        server = context.message.server
        author = context.message.author
        instructions = 'Thank you for using Grenzpolizei! However, this cog requires some setting up and a dozen or so questions will be asked.\n'
        instructions += 'You\'re required to answer them with either **\'yes\'** or **\'no\'** answers.\n\n'
        instructions += 'You get **2 minutes** to answer each question. If not answered it will be defaulted to **\'no\'**.\n\n'
        instructions += 'Then you\'re required to give a channel for each event category, these categories are:\n\n'
        instructions += '**- member events**\n**- message events**\n**- server events**\n**- warning events.**\n\n'
        instructions += 'Each channel _needs_ to be a channel mention, otherwise it won\'t work. You can use the same channel for all event types.\n'
        instructions += 'Make also sure to give proper permissions to the bot to post and embed messages in these channels.\n\n'
        instructions += '**Good luck!**'

        embed = discord.Embed(title='**Welcome to the setup for Grenzpolizei**', description=instructions, color=self.green)
        await self.bot.say(server, embed=embed)
        await asyncio.sleep(10)
        if server.id not in self.settings:
            self.settings[server.id] = {}
        if server.id in self.settings:
            events = {}
            channels = {}

            # Member events
            events['on_member_join'] = await self._yes_no('Do you want to track members joining? [y]es/[n]o', author)
            events['on_member_ban'] = await self._yes_no('Do you want to track members being banned? [y]es/[n]o', author)
            events['on_member_unban'] = await self._yes_no('Do you want to track members being unbanned? [y]es/[n]o', author)
            events['on_member_remove'] = await self._yes_no('Do you want to track members leaving this server? [y]es/[n]o', author)
            events['on_member_update'] = await self._yes_no('Do you want to track member changes? [y]es/[n]o', author)
            events['on_voice_state_update'] = await self._yes_no('Do you want to track voice channel changes? [y]es/[n]o', author)

            # Message events
            events['on_message_delete'] = await self._yes_no('Do you want to track message deletion? [y]es/[n]o', author)
            events['on_message_edit'] = await self._yes_no('Do you want to track message editing? [y]es/[n]o', author)

            # Server events
            events['on_channel_create'] = await self._yes_no('Do you want to track channel creation? [y]es/[n]o', author)
            events['on_channel_delete'] = await self._yes_no('Do you want to track channel deletion? [y]es/[n]o', author)
            events['on_channel_update'] = await self._yes_no('Do you want to track channel updates? [y]es/[n]o', author)

            events['on_server_role_create'] = await self._yes_no('Do you want to track role creation? [y]es/[n]o', author)
            events['on_server_role_delete'] = await self._yes_no('Do you want to track role deletion? [y]es/[n]o', author)
            events['on_server_role_update'] = await self._yes_no('Do you want to track role updates? [y]es/[n]o', author)

            # Warning events
            events['on_warning'] = await self._yes_no('Do you want to track member warnings? [y]es/[n]o', author)
            events['on_kick'] = await self._yes_no('Do you want to track member kick warnings? [y]es/[n]o', author)
            events['on_ban'] = await self._yes_no('Do you want to track member ban warnings? [y]es/[n]o', author)

            if any([events['on_member_join'], events['on_member_ban'], events['on_member_unban'], events['on_member_remove'], events['on_voice_state_update']]):
                channels['member_event_channel'] = await self._what_channel('Which channel do you want to use for member events? (please mention the channel)', author)
            else:
                channels['member_event_channel'] = False

            if any([events['on_message_delete'], events['on_message_edit']]):
                channels['message_event_channel'] = await self._what_channel('Which channel do you want to use for message events? (please mention the channel)', author)
            else:
                channels['message_event_channel'] = False

            if any([events['on_channel_create'], events['on_channel_delete'], events['on_channel_update'], events['on_server_role_create'],
                    events['on_server_role_delete'], events['on_server_role_update']]):
                channels['server_event_channel'] = await self._what_channel('Which channel do you want to use for server events? (please mention the channel)', author)
            else:
                channels['server_event_channel'] = False

            if any([events['on_warning'], events['on_kick'], events['on_ban']]):
                channels['mod_event_channel'] = await self._what_channel('Which channel do you want to use for modding events? (please mention the channel)', author)
            else:
                channels['mod_event_channel'] = False

            self.settings[server.id]['channels'] = channels
            self.settings[server.id]['events'] = events

            await self._save_settings()

            return True
        else:
            return False

    @commands.group(pass_context=True, name='border', aliases=['grenzpolizei', 'polizei', 'police'])
    async def _grenzpolizei(self, context):
        if context.invoked_subcommand is None:
            await send_cmd_help(context)

    @_grenzpolizei.command(pass_context=True, name='setup')
    @checks.mod_or_permissions(administrator=True)
    async def _setup(self, context):
        '''
        Setup your server for Grenzpolizei
        '''
        new_server = await self._setup_questions(context)
        if new_server:
            message = 'You\'re all set up right now!'
        else:
            message = 'Something didn\'t go quite right.'
        await self.bot.say(message)

    @_grenzpolizei.command(pass_context=True, name='ignoremember')
    @checks.mod_or_permissions(administrator=True)
    async def _ignoremember(self, context, member: discord.Member):
        '''
        Ignore a member, this is a toggle
        '''
        server = context.message.server
        done = await self.ignoremember(server, member)
        message = done
        await self.bot.say(message)

    @_grenzpolizei.command(pass_context=True, name='ignorechannel')
    @checks.mod_or_permissions(administrator=True)
    async def _ignorechannel(self, context, channel: discord.Channel):
        '''
        Ignore a channel, this is a toggle
        '''
        server = context.message.server
        done = await self.ignorechannel(server, channel)
        message = done
        await self.bot.say(message)

    @_grenzpolizei.command(pass_context=True, name='warn', aliases=['strike'])
    @checks.mod_or_permissions(kick_members=True)
    async def _warn(self, context, member: discord.Member, *, reason):
        '''
        Give out a warning
        '''
        author = context.message.author
        server = context.message.server
        warn = await self.on_warning(server, author, member, reason)
        if warn:
            message = 'Done!'
        else:
            message = 'Something didn\'t go quite right.'
        await self.bot.say(message)

    @_grenzpolizei.command(pass_context=True, name='kick', aliases=['boot'])
    @checks.mod_or_permissions(kick_members=True)
    async def _kick_member(self, context, member: discord.Member, *, reason):
        '''
        Put on your boots and get it dirty.
        '''
        author = context.message.author
        server = context.message.server
        await self.bot.kick(member)
        warn = await self.on_kick(server, author, member, reason)
        if warn:
            message = 'Done!'
        else:
            message = 'Something didn\'t go quite right.'
        await self.bot.say(message)

    @_grenzpolizei.command(pass_context=True, name='ban', aliases=['hammer'])
    @checks.mod_or_permissions(ban_members=True)
    async def _ban_member(self, context, member: discord.Member, *, reason):
        '''
        Grab your hammer and swing it \'round.
        '''
        author = context.message.author
        server = context.message.server
        await self.bot.ban(member)
        warn = await self.on_ban(server, author, member, reason)
        if warn:
            message = 'Done!'
        else:
            message = 'Something didn\'t go quite right.'
        await self.bot.say(message)

    async def on_warning(self, server, mod, member, reason):
        if await self._validate_event(server) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=self.orange)
            embed.set_author(name='{0.name}#{0.discriminator} ({0.id}) has been warned'.format(member), icon_url=avatar)
            embed.add_field(name='**Mod**', value=mod.name, inline=False)
            embed.add_field(name='**Reason**', value=reason)
            await self._send_message_to_channel(server, embed=embed)
            return True
        else:
            return False

    async def on_kick(self, server, mod, member, reason):
        if await self._validate_event(server) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=self.red)
            embed.set_author(name='{0.name}#{0.discriminator} ({0.id}) has been kicked'.format(member), icon_url=avatar)
            embed.add_field(name='**Mod**', value=mod.name, inline=False)
            embed.add_field(name='**Reason**', value=reason)
            await self._send_message_to_channel(server, embed=embed)
            return True
        else:
            return False

    async def on_ban(self, server, mod, member, reason):
        if await self._validate_event(server) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=self.red)
            embed.set_author(name='{0.name}#{0.discriminator} ({0.id}) has been banned'.format(member), icon_url=avatar)
            embed.add_field(name='**Mod**', value=mod.name, inline=False)
            embed.add_field(name='**Reason**', value=reason)
            await self._send_message_to_channel(server, embed=embed)
            return True
        else:
            return False

    async def on_member_join(self, member):
        server = member.server
        if await self._validate_event(server) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=self.green, description='**{0.name}#{0.discriminator}** ({0.id})'.format(member))
            embed.set_author(name='Member joined', icon_url=avatar)
            await self._send_message_to_channel(server, embed=embed)

    async def on_member_ban(self, member):
        server = member.server
        if await self._validate_event(server) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=self.red, description='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(member))
            embed.set_author(name='Member banned', icon_url=avatar)
            await self._send_message_to_channel(server, embed=embed)

    async def on_member_unban(self, server, member):
        if await self._validate_event(server) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=self.orange, description='**{0.name}#{0.discriminator}** ({0.id})'.format(member))
            embed.set_author(name='Member unbanned', icon_url=avatar)
            await self._send_message_to_channel(server, embed=embed)

    async def on_member_remove(self, member):
        server = member.server
        if await self._validate_event(server) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=self.red, description='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(member))
            embed.set_author(name='Member left', icon_url=avatar)
            await self._send_message_to_channel(server, embed=embed)

    async def on_member_update(self, before, after):
        server = after.server
        member = after
        if await self._ignore(server, member=member):
            if await self._validate_event(server) and after.id != self.bot.user.id:
                if before.name != after.name:
                    embed = discord.Embed(color=self.blue, description='From **{0.name}** ({0.id}) to **{1.name}**'.format(before, after))
                    embed.set_author(name='Name changed', icon_url=server.icon_url)
                    await self._send_message_to_channel(server, embed=embed)
                if before.nick != after.nick:
                    embed = discord.Embed(color=self.blue, description='From **{0.nick}** ({0.id}) to **{1.nick}**'.format(before, after))
                    embed.set_author(name='Nickname changed', icon_url=server.icon_url)
                    await self._send_message_to_channel(server, embed=embed)
                if before.roles != after.roles:
                    if len(before.roles) > len(after.roles):
                        for role in before.roles:
                            if role not in after.roles:
                                embed = discord.Embed(color=self.blue, description='**{0.display_name}** ({0.id}) lost the **{1.name}** role'.format(before, role))
                                embed.set_author(name='Role removed', icon_url=server.icon_url)
                    elif len(before.roles) < len(after.roles):
                        for role in after.roles:
                            if role not in before.roles:
                                embed = discord.Embed(color=self.blue, description='**{0.display_name}** ({0.id}) got the **{1.name}** role'.format(before, role))
                                embed.set_author(name='Role applied', icon_url=server.icon_url)
                    await self._send_message_to_channel(server, embed=embed)

    async def on_message_delete(self, message):
        server = message.server
        member = message.author
        channel = message.channel
        timestamp = datetime.utcnow()
        if await self._ignore(server, member=member, channel=channel):
            if await self._validate_event(server) and member.id != self.bot.user.id:
                embed = discord.Embed(color=self.red)
                avatar = member.avatar_url if member.avatar else member.default_avatar_url
                embed.set_author(name='Message removed', icon_url=avatar)
                embed.add_field(name='**Member**', value='{0.display_name}#{0.discriminator} ({0.id})'.format(member))
                embed.add_field(name='**Channel**', value=message.channel.name)
                embed.add_field(name='**Message timestamp**', value=message.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                embed.add_field(name='**Removal timestamp**', value=timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                if message.content:
                    embed.add_field(name='**Message**', value=message.content, inline=False)
                if message.attachments:
                    for attachment in message.attachments:
                        embed.add_field(name='**Attachment**', value='[{filename}]({url})'.format(**attachment), inline=True)
                await self._send_message_to_channel(server, embed=embed)

    async def on_message_edit(self, before, after):
        server = after.server
        member = after.author
        channel = after.channel
        timestamp = datetime.utcnow()
        if not channel.is_private:
            if await self._ignore(server, member=member, channel=channel):
                if await self._validate_event(server) and member.id != self.bot.user.id and before.clean_content != after.clean_content:
                    embed = discord.Embed(color=self.blue)
                    avatar = member.avatar_url if member.avatar else member.default_avatar_url
                    embed.set_author(name='Message changed'.format(member), icon_url=avatar)
                    embed.add_field(name='**Member**', value='{0.display_name}#{0.discriminator}\n({0.id})'.format(member))
                    embed.add_field(name='**Channel**', value=before.channel.name)
                    embed.add_field(name='**Message timestamp**', value=before.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                    embed.add_field(name='**Edit timestamp**', value=timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                    embed.add_field(name='**Before**', value=before.content, inline=False)
                    embed.add_field(name='**After**', value=after.content, inline=False)
                    await self._send_message_to_channel(server, embed=embed)

    async def on_channel_create(self, channel):
        if not channel.is_private:
            server = channel.server
            if await self._validate_event(server):
                embed = discord.Embed(color=self.green)
                embed.set_author(name='A new channel has been created: #{0.name}'.format(channel), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)

    async def on_channel_delete(self, channel):
        if not channel.is_private:
            server = channel.server
            if await self._validate_event(server):
                embed = discord.Embed(color=self.red)
                embed.set_author(name='A channel has been deleted: #{0.name}'.format(channel), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)

    async def on_channel_update(self, before, after):
        if not after.is_private:
            server = after.server
            if await self._validate_event(server):
                if before.name != after.name:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='#{0.name} renamed to #{1.name}'.format(before, after), icon_url=server.icon_url)
                    await self._send_message_to_channel(server, embed=embed)
                if before.topic != after.topic:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='#{0.name} topic changed from \'{0.topic}\' to \'{1.topic}\''.format(before, after), icon_url=server.icon_url)
                    await self._send_message_to_channel(server, embed=embed)
                if before.position != after.position:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='#{0.name} moved from {0.position} to {1.position}'.format(before, after), icon_url=server.icon_url)
                    await self._send_message_to_channel(server, embed=embed)

    async def on_server_role_create(self, role):
        server = role.server
        if await self._validate_event(server):
            embed = discord.Embed(color=self.green)
            embed.set_author(name='Role created: {0.name}'.format(role), icon_url=server.icon_url)
            await self._send_message_to_channel(server, embed=embed)

    async def on_server_role_delete(self, role):
        server = role.server
        if await self._validate_event(server):
            embed = discord.Embed(color=self.red)
            embed.set_author(name='Role deleted: {0.name}'.format(role), icon_url=server.icon_url)
            await self._send_message_to_channel(server, embed=embed)

    async def on_server_role_update(self, before, after):
        server = after.server
        if await self._validate_event(server):
            if before.name != after.name:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Role {0.name} renamed to {1.name}'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)
            if before.color != after.color:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Role color \'{0.name}\' changed from {0.color} to {1.color}'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)
            if before.mentionable != after.mentionable:
                embed = discord.Embed(color=self.blue)
                if after.mentionable:
                    embed.set_author(name='Role \'{0.name}\' is now mentionable'.format(after), icon_url=server.icon_url)
                else:
                    embed.set_author(name='Role \'{0.name}\' is no longer mentionable'.format(after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)
            if before.hoist != after.hoist:
                embed = discord.Embed(color=self.blue)
                if after.hoist:
                    embed.set_author(name='Role \'{0.name}\' is now shown seperately'.format(after), icon_url=server.icon_url)
                else:
                    embed.set_author(name='Role \'{0.name}\' is no longer shown seperately'.format(after), icon_url=server.icon_url)
            if before.permissions != after.permissions:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Role permissions \'{0.name}\' changed from {0.permissions.value} to {1.permissions.value}'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)
            if before.position != after.position:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Role position \'{0}\' changed from {0.position} to {1.position}'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)

    async def on_server_update(self, before, after):
        server = after.server
        if await self._validate_event(server):
            if before.owner != after.owner:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Server owner changed from {0.owner.name} (id {0.owner.id}) to {1.owner.name} (id {1.owner.id})'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)
            if before.region != after.region:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Server region changed from {0.region} to {1.region}'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)
            if before.name != after.name:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Server name changed from {0.name} to {1.name}'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)
            if before.icon_url != after.icon_url:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name='Server icon changed from {0.icon_url} to {1.icon_url}'.format(before, after), icon_url=server.icon_url)
                await self._send_message_to_channel(server, embed=embed)

    async def on_voice_state_update(self, before, after):
        server = after.server
        member = after
        await self._ignore_server_check(server)
        if await self._ignore(server, member=member):
            if await self._validate_event(server):
                if not before.voice.is_afk and after.voice.is_afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{0.display_name} is idle and has been sent to #{0.voice_channel}'.format(after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)
                elif before.voice.is_afk and not after.voice.is_afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{0.display_name} is active again in #{0.voice_channel}'.format(after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)
                if not before.voice.self_mute and after.voice.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{0.display_name} muted themselves in #{0.voice_channel}'.format(after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)
                elif before.voice.self_mute and not after.voice.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{0.display_name} unmuted themselves in #{0.voice_channel}'.format(after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)
                if not before.voice.self_deaf and after.voice.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{0.display_name} deafened themselves in #{0.voice_channel}'.format(after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)
                elif before.voice.self_deaf and not after.voice.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{0.display_name} undeafened themselves in #{0.voice_channel}'.format(after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)
                if not before.voice.voice_channel and after.voice.voice_channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{0.display_name} joined voice channel #{0.voice_channel}'.format(after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)
                elif before.voice.voice_channel and not after.voice.voice_channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name='{1.display_name} left voice channel #{0.voice_channel}'.format(before, after), icon_url=after.avatar_url if after.avatar_url else after.default_avatar_url)
                    await self._send_message_to_channel(server, embed=embed)


def check_folder():
    if not os.path.exists('data/grenzpolizei'):
        print('Creating data/grenzpolizei folder...')
        os.makedirs('data/grenzpolizei')


def check_file():
    data = {}

    data['db_version'] = DB_VERSION
    settings_file = 'data/grenzpolizei/settings.json'
    ignore_file = 'data/grenzpolizei/ignore.json'
    if not dataIO.is_valid_json(settings_file):
        print('Creating default settings.json...')
        dataIO.save_json(settings_file, data)
    else:
        check = dataIO.load_json(settings_file)
        if 'db_version' in check:
            if check['db_version'] < DB_VERSION:
                data = {}
                data['db_version'] = DB_VERSION
                print('GRENZPOLIZEI: Database version too old, please rerun the setup!')
                dataIO.save_json(settings_file, data)

    if not dataIO.is_valid_json(ignore_file):
        print('Creating default ignore.json...')
        dataIO.save_json(ignore_file, {})


def setup(bot):
    check_folder()
    check_file()
    cog = Grenzpolizei(bot)
    bot.add_cog(cog)
