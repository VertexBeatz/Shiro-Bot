from discord.ext import commands
from .utils import checks
from raven import Client
from raven.conf import setup_logging
from raven_aiohttp import AioHttpTransport
from raven.handlers.logging import SentryHandler
import os
from cogs.utils.dataIO import dataIO
import logging

log = logging.getLogger("red.sentryio")


class SentryIO:
    """Sentry Debugging"""

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.load_json('data/sentryio/config.json')
        self.clientid = self.config.get("clientid", "")

        self.raven = None
        self.load_sentry()

    @property
    def clientid(self):
        return self.config.get("clientid", "")

    @clientid.setter
    def clientid(self, value):
        self.config["clientid"] = value

        dataIO.save_json('data/sentryio/config.json', self.config)

        self.load_sentry()

    def load_sentry(self):
        if self.clientid == "":
            return

        self.raven = Client(self.clientid, transport=AioHttpTransport)
        self.handler = SentryHandler(self.raven)
        setup_logging(self.handler)
        log.debug("Sentry handler activated.")

    @commands.group()
    @checks.is_owner()
    async def sentryio(self):
        """
        Sentry.io Client stuff
        """

    @sentryio.command(name="clientid", pass_context=True)
    async def _sentry_io_clientid(self, ctx, clientid):
        """
        Set up sentry.io client id
        """
        self.clientid = clientid
        await self.bot.say("Saved.")


def check_files():
    if not os.path.exists('data/sentryio/config.json'):
        try:
            os.mkdir('data/sentryio')
        except FileExistsError:
            pass
        dataIO.save_json('data/sentryio/config.json', {})


def setup(bot):
    check_files()
    n = SentryIO(bot)
    bot.add_cog(n)
