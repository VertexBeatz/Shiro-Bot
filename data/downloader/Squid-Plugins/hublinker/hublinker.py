import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import fileIO
from __main__ import send_cmd_help
import os
import logging
import copy

log = logging.getLogger("red.hublinker")
log.setLevel(logging.WARNING)


class HubLinker:
    """This will sync all roles and assignments from ONE master server to all
    slaves.

    BE FOREWARNED: DO NOT FUCK WITH THE ROLES ON THE SLAVE SERVERS.
    """

    def __init__(self, bot):
        self.bot = bot
        self.links = fileIO('data/hublinker/links.json', 'load')

    def save_links(self):
        fileIO('data/hublinker/links.json', 'save', self.links)
        log.debug('saved hublinker links:\n\t{}'.format(self.links))

    @commands.group(no_pm=True, pass_context=True)
    @checks.serverowner_or_permissions(manage_roles=True)
    async def hublink(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @hublink.command(no_pm=True, pass_context=True)
    async def master(self, ctx):
        """Makes this server a 'master' that others copy their roles from."""
        sid = ctx.message.server.id
        if sid not in self.links:
            self.links[sid] = {'ENABLED': False, 'SLAVES': []}
        await self.bot.say('Server ID: {}'.format(sid))
        self.save_links()
        log.debug("added master: {}".format(sid))

    @hublink.command(no_pm=True, pass_context=True)
    async def remove(self, ctx):
        """Removes this server from hublinker control"""
        server = ctx.message.server
        sid = server.id

        all_slaves = []
        for master in self.links:
            for slave in self.links[master]['SLAVES']:
                all_slaves.append(slave)

        if sid in self.links:
            del self.links[sid]
            await self.bot.say("Master removed.")
        elif sid in all_slaves:
            for master in self.links:
                if sid in self.links[master]['SLAVES']:
                    self.links[master]["SLAVES"].remove(sid)
                    await self.bot.say("Slave removed.")
                    break
        else:
            await self.bot.say('This server is neither a master nor a slave.')
        self.save_links()

    @hublink.command(no_pm=True, pass_context=True)
    async def slave(self, ctx, master_server_id):
        """Makes this server a 'slave' to an already created master server."""
        if master_server_id not in self.links:
            await self.bot.say('That master server doesn\'t exist or is not'
                               ' set up yet.')
            return
        server = ctx.message.server
        if server.id in self.links[master_server_id]['SLAVES']:
            await self.bot.say('This server is already set up to be a slave.')
            return
        self.links[master_server_id]['SLAVES'].append(server.id)
        log.debug('slave {} to master {}'.format(server.id, master_server_id))
        self.save_links()

    @hublink.command(no_pm=True, pass_context=True)
    async def toggle(self, ctx):
        """Toggles whether the links coming from this server are enabled."""
        server = ctx.message.server
        sid = server.id
        if sid in self.links:
            old = self.links[sid]['ENABLED']
            self.links[sid]['ENABLED'] = not old
            if old:
                log.debug('master {} disabled'.format(sid))
                await self.bot.say('Master link disabled.')
            else:
                try:
                    self._slave_role_check(server)
                except:
                    await self.bot.say("You MUST put the 'Squid' role above"
                                       " ALL OTHERS on ALL slave servers.")
                    return
                log.debug('master {} enabled'.format(sid))
                await self.bot.say('Master link enabled.')
                for slave in self.links[sid]['SLAVES']:
                    discord.compat.create_task(self.initial_linker(sid, slave))
            self.save_links()
        else:
            await self.bot.say('This server is not a master.')

    @hublink.command(no_pm=True, pass_context=True)
    async def init(self, ctx):
        server = ctx.message.server
        sid = server.id

        all_slaves = []
        for master in self.links:
            for slave in self.links[master]['SLAVES']:
                all_slaves.append(slave)

        if sid in self.links:
            for slave in self.links[sid]['SLAVES']:
                try:
                    self._slave_role_check(server)
                except:
                    await self.bot.say("You MUST put the 'Squid' role above"
                                       " ALL OTHERS on ALL slave servers.")
                else:
                    await self.initial_linker(sid, slave)
        elif sid in all_slaves:
            for master in self.links:
                if sid in self.links[master]['SLAVES']:
                    ms = discord.utils.get(self.bot.servers, id=master)
                    if ms is None:
                        return

                    try:
                        self._slave_role_check(ms)
                    except:
                        await self.bot.say(
                            "You MUST put the 'Squid' role above"
                            " ALL OTHERS on ALL slave servers.")
                    else:
                        log.debug('forcing init on slave '
                                  '{} from master {}'.format(sid, master))
                        await self.initial_linker(master, sid)
                        break
        else:
            await self.bot.say('This server is neither a master nor a slave.')

    async def initial_linker(self, master, slave):
        master = discord.utils.get(self.bot.servers, id=master)
        slave = discord.utils.get(self.bot.servers, id=slave)
        if master is None or slave is None:
            return

        my_role = discord.utils.find(lambda r: r.name.lower() == "squid",
                                     slave.roles)
        if my_role is None:
            role_dict = {}
            role_dict['permissions'] = \
                discord.Permissions(permissions=36826127)
            role_dict['name'] = "Squid"
            my_server_role = await self.bot.create_role(slave, **role_dict)
            await self.bot.add_roles(slave.me, my_server_role)

        log.debug('Slave roles:\n\t{}'.format(
            [role.name for role in slave.roles]))

        await self._delete_all_roles(slave)

        log.debug('Slave roles:\n\t{}'.format(
            [role.name for role in slave.roles]))

        await self._create_all_roles(slave, master)

        # We only really care about the online people, this way we *hopefully*
        # don't get ourselves rate-limited on large servers.

        online_master_members = [m for m in master.members
                                 if m.status == discord.Status.online]
        omm_withrole = [m for m in online_master_members if len(m.roles) > 1]
        ommwr_in_slave = [m for m in omm_withrole if m in slave.members]

        log.debug('members to give role to RN:\n\t{}'.format(
            [m.name for m in ommwr_in_slave]))

        for m in ommwr_in_slave:
            slave_member = discord.utils.get(slave.members, id=m.id)
            to_add = []
            for mrole in m.roles:
                if mrole.name.lower() == "@everyone" \
                        or mrole.name.lower() == "squid":
                    continue
                log.debug(self._matching_role(slave, mrole))
                to_add.append(self._matching_role(slave, mrole))
            log.debug('adding roles to {0.name} on {1.id}:\n\t{2}'.format(
                slave_member, slave, [r.name for r in to_add]))
            discord.compat.create_task(
                self.bot.add_roles(slave_member, *to_add))

    async def _delete_all_roles(self, server):
        roles = copy.deepcopy(server.roles)
        for role in roles:
            if role.name.lower() == "@everyone" or \
                    role.name.lower() == "squid":
                log.debug('Skipping delete role {}'.format(role.name))
                continue
            await self.bot.delete_role(server, role)
            log.debug('deleted role {} from {}'.format(role.name, server.name))

    async def _create_all_roles(self, slave, master):
        for role in master.roles:
            if role.name.lower() == "@everyone" or \
                    role.name.lower() == "squid":
                continue
            roleattrs = self._explode_role(role)
            await self.bot.create_role(slave, **roleattrs)
            log.debug('created role {} on {}'.format(role.name, slave.name) +
                      ' with attrs:\n\t{}'.format(roleattrs))

    def _exists_and_enabled(self, sid):
        if sid in self.links and self.links[sid]['ENABLED']:
            return True
        return False

    def _has_manage_role(self, sid):
        server = discord.utils.get(self.bot.servers, id=sid)
        if server is None:
            return False
        my_roles = server.me.roles
        my_roles_with_manage_roles = \
            list(filter((lambda r: r.permissions.manage_roles), my_roles))
        if len(my_roles_with_manage_roles) > 0:
            return True
        return False

    def _get_server_from_role(self, role):
        return discord.utils.find((lambda s: role in s.roles),
                                  self.bot.servers)

    def _matching_role(self, inserver, inrole):
        if not isinstance(inserver, discord.Server):
            inserver = self._server_from_id(inserver)
        if inserver is None:
            return None

        roleattrs = self._explode_role(inrole)
        roleattrs['permissions__value'] = roleattrs['permissions'].value
        del roleattrs['permissions']
        roleattrs['colour__value'] = roleattrs['colour'].value
        del roleattrs['colour']

        log.debug(roleattrs)
        outrole = discord.utils.get(inserver.roles, **roleattrs)
        return outrole

    def _slave_role_check(self, master):
        mid = master.id
        if mid not in self.links:
            return

        for sid in self.links[mid]["SLAVES"]:
            slave = discord.utils.get(self.bot.servers, id=sid)
            if slave is None:
                continue

            highest_role = sorted(slave.roles, key=lambda r: r.position,
                                  reverse=True)[0]
            if highest_role.name != "Squid":
                raise Exception
            elif not highest_role.permissions.manage_roles:
                raise Exception

    def _explode_role(self, role):
        ret = {}
        ret['name'] = role.name
        ret['permissions'] = role.permissions
        ret['colour'] = role.colour
        ret['hoist'] = role.hoist
        return ret

    def _role_equality(self, r1, r2):
        if r1.name != r2.name:
            return False
        if r1.permissions != r2.permissions:
            return False
        if r1.colour != r2.colour:
            return False
        if r1.hoist != r2.hoist:
            return False

    def _server_from_id(self, id):
        if isinstance(id, list):
            return map((lambda s: discord.utils.get(self.bot.servers, id=s)),
                       id)
        return discord.utils.get(self.bot.servers, id=id)

    async def _new_role_from_master(self, server, before, after):
        role_add = []
        for role in after.roles:
            if role.name == "@everyone":
                continue
            before_role = discord.utils.get(before.roles, id=role.id)
            if before_role is None:
                role_add.append(role)

        log.debug('adding roles {}'.format([r.name for r in role_add]))

        role_del = []
        for role in before.roles:
            if role.name == "@everyone":
                continue
            after_role = discord.utils.get(after.roles, id=role.id)
            if after_role is None:
                role_del.append(role)

        log.debug('deleting roles {}'.format([r.name for r in role_del]))

        for role in role_add:
            to_add = map(lambda s: (s, self._matching_role(s, role)),
                         self.links[server.id]['SLAVES'])
            for (s, r) in to_add:
                s = discord.utils.get(self.bot.servers, id=s)
                if s is None or r is None:
                    log.debug('ADD slve or role not found, {} {}'.format(
                        s, r))
                    continue
                member = discord.utils.get(s.members, id=after.id)
                if member is None:
                    continue
                log.debug('adding {} to {} on {}'.format(r.name, member.name,
                                                         member.server.id))
                await self.bot.add_roles(member, r)

        for role in role_del:
            to_del = map(lambda s: (s, self._matching_role(s, role)),
                         self.links[server.id]['SLAVES'])
            for (s, r) in to_del:
                s = discord.utils.get(self.bot.servers, id=s)
                if s is None or r is None:
                    continue
                member = discord.utils.get(s.members, id=after.id)
                if member is None:
                    continue
                log.debug('deleting {} to {} on {}'.format(r.name, member.name,
                                                           member.server.id))
                discord.compat.create_task(self.bot.remove_roles(member, r))

    async def _status_role_compare(self, master, before, after):
        if before.status != discord.Status.online and after.status == \
                discord.Status.online:
            pass
        else:
            return
        log.debug('{} came online'.format(after.name))
        slaves = self._server_from_id(self.links[master.id]['SLAVES'])
        for slave in slaves:
            slave_member = discord.utils.get(slave.members, id=after.id)
            if slave_member is None:
                continue
            for role in after.roles:
                slave_role = self._matching_role(slave, role)
                if slave_role and slave_role not in slave_member.roles:
                    discord.compat.create_task(self.bot.add_roles(
                        slave_member, slave_role))

    async def role_create(self, role):
        server = role.server
        if not self._exists_and_enabled(server.id):
            return
        if not self._has_manage_role(server.id):
            return
        sid = server.id
        log.debug('new role "{}" on master {}'.format(role.name, sid))
        for slave in self.links[sid]['SLAVES']:
            slave_server = discord.utils.get(self.bot.servers,
                                             id=slave)
            if slave_server is None:
                continue
            role_dict = self._explode_role(role)
            discord.compat.create_task(self.bot.create_role(slave_server,
                                                            **role_dict))

    async def role_delete(self, role):
        server = role.server
        if not self._exists_and_enabled(server.id):
            return
        if not self._has_manage_role(server.id):
            return
        to_delete = map(lambda s: (s, self._matching_role(s, role)),
                        self.links[server.id]['SLAVES'])
        for (s, r) in to_delete:
            s = self._server_from_id(s)
            if s is None or r is None:
                continue
            discord.compat.create_task(self.bot.delete_role(s, r))

    async def role_edit(self, before, after):
        server = self._get_server_from_role(before)
        if server is None:
            return
        if not self._exists_and_enabled(server.id):
            return
        if not self._has_manage_role(server.id):
            return
        log.debug('new edit on master {}:\n\tBefore: {}\n\tAfter: {}'.format(
            server.id, self._explode_role(before), self._explode_role(after)))
        to_edit = map(lambda s: (s, self._matching_role(s, before)),
                      self.links[server.id]['SLAVES'])
        for (s, r) in to_edit:
            s = self._server_from_id(s)
            if s is None or r is None:
                continue
            discord.compat.create_task(
                self.bot.edit_role(s, r, **self._explode_role(after)))

    async def member_join(self, member):
        slave = member.server
        master = None
        for mid in self.links:
            for sid in self.links[mid]['SLAVES']:
                if sid == slave.id:
                    master = mid
        master = discord.utils.get(self.bot.servers, id=master)
        if master is None:
            return
        log.debug('{} joined {} with master {}'.format(member.name,
                                                       slave.name,
                                                       master.name))
        master_member = discord.utils.get(master.members, id=member.id)
        if master_member is None:
            return
        master_member_roles = master_member.roles
        for master_role in master_member_roles:
            if master_role.name.lower() == "@everyone":
                continue
            role = self._matching_role(slave, master_role)
            if role is None:
                role = await self.bot.create_role(
                    slave, **self._explode_role(master_role)
                )
            await self.bot.add_roles(member, role)

    async def member_update(self, before, after):
        server = after.server
        if server is None:
            return
        if not self._exists_and_enabled(server.id):
            return
        elif not self._has_manage_role(server.id):
            return

        log.debug('member {} update on master {}'.format(after.name,
                                                         server.id))

        await self._new_role_from_master(server, before, after)

        await self._status_role_compare(server, before, after)


def check_folder():
    if not os.path.exists('data/hublinker'):
        os.mkdir('data/hublinker')


def check_files():
    f = 'data/hublinker/links.json'
    if not os.path.exists(f):
        fileIO(f, 'save', {})


def setup(bot):
    check_folder()
    check_files()
    n = HubLinker(bot)
    bot.add_cog(n)
    bot.add_listener(n.role_create, 'on_server_role_create')
    bot.add_listener(n.role_delete, 'on_server_role_delete')
    bot.add_listener(n.role_edit, 'on_server_role_update')
    bot.add_listener(n.member_join, 'on_member_join')
    bot.add_listener(n.member_update, 'on_member_update')
