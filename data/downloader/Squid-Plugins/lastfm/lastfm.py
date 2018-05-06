from discord.ext import commands

import os
import asyncio
import time

from cogs.utils.dataIO import fileIO
from __main__ import send_cmd_help

try:
    import pylast
except:
    pylast = None


class Scrobbler(object):
    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO('data/lastfm/settings.json', 'load')
        self.valid_settings = self.check_settings()
        if not self.valid_settings:
            raise RuntimeError("You need to set your lastfm settings.")
        self.network = self.setup_network()
        self.audio = None
        self.last_title = ""

    def setup_network(self):
        api_key = self.settings.get('APIKEY')
        api_secret = self.settings.get('APISECRET')
        username = self.settings.get('USERNAME')
        password = pylast.md5(self.settings.get('PASSWORD'))
        net = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret,
                                   username=username, password_hash=password)
        return net

    def check_settings(self):
        for k, v in self.settings.items():
            if v == '':
                print("Error: You need to set your {} in ".format(k) +
                      "data/lastfm/settings.json")
                return False
        return True

    @commands.group(pass_context=True)
    async def lastfmset(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @lastfmset.command(pass_context=True, name="enable")
    async def _lastfmset_enabled(self, ctx):
        if 'ENABLED' not in self.settings:
            self.settings['ENABLED'] = True
            await self.bot.say('Scrobbler enabled.')
        else:
            curr = self.setting['ENABLED']
            self.setting['ENABLED'] = (not curr)
            await self.bot.say('Scrobbler enabled? {}'.format((not curr)))
        fileIO('data/lastfm/settings.json', 'save', self.settings)

    async def audio_watcher(self):
        await self.bot.wait_until_ready()
        while 'Scrobbler' in self.bot.cogs:
            self.audio = self.bot.get_cog('Audio')
            if self.audio:
                if self.audio.downloader["DONE"]:
                    if self.audio.downloader["TITLE"] != self.last_title \
                            and self.audio.music_player.is_playing():
                        self.last_title = self.audio.downloader["TITLE"]
                        title = self.last_title
                        artist = "Wish I knew"
                        timestamp = int(time.time())
                        try:
                            splitted = self.last_title.split(' - ')
                            title = splitted[1]
                            artist = splitted[0]
                        except:
                            pass
                        self.network.scrobble(title=title,
                                              artist=artist,
                                              timestamp=timestamp)
                await asyncio.sleep(30)
            else:
                print('Audio not loaded!')
                await asyncio.sleep(15)


def check_folders():
    if not os.path.exists('data/lastfm'):
        print('Creating data/lastfm folder.')
        os.mkdir('data/lastfm')


def check_files():
    s = {'APIKEY': '', 'APISECRET': '', 'USERNAME': '', 'PASSWORD': ''}

    f = "data/lastfm/settings.json"
    if not fileIO(f, "check"):
        print("Creating default lastfm's settings.json...")
        fileIO(f, "save", s)


def setup(bot):
    if pylast is None:
        raise NameError("You need to run `pip3 install pylast`")
    check_folders()
    check_files()
    n = Scrobbler(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.audio_watcher())
