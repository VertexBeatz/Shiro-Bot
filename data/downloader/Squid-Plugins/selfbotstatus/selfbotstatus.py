import keyboard as kb
import time
import discord
import asyncio


class SelfBotStatus:
    def __init__(self, bot):
        self.bot = bot

        self.is_online = True

        self._last_time = 0

        kb.hook(self.kb_press)

        self.status_task = None
        self.start = False

    def __unload(self):
        try:
            self.status_task.cancel()
        except AttributeError:
            pass

    def kb_press(self, event):
        if not self.start:
            return

        etime = event.time
        if self.is_online is True:
            try:
                self.status_task.cancel()
            except AttributeError:
                pass
            self.status_task = self.bot.loop.create_task(
                self._set_idle(etime + 300))
        elif self.is_online is False:
            self.status_task = self.bot.loop.create_task(
                self._set_online())
        self._last_time = etime

    def _get_game(self):
        try:
            me = list(self.bot.servers)[0].me
            game = me.game
        except IndexError:
            game = None

        return game

    async def _set_idle(self, ttl):
        while time.time() < ttl:
            asyncio.sleep(1)
        game = self._get_game()
        await self.bot.change_presence(game=game, status=discord.Status.idle,
                                       afk=True)
        self.is_online = False

    async def _set_online(self, ttl=0):
        while time.time() < ttl:
            asyncio.sleep(1)
        game = self._get_game()
        await self.bot.change_presence(game=game, status=discord.Status.online,
                                       afk=False)
        self.is_online = True

    async def on_ready(self):
        self.start = True


def setup(bot):
    bot.add_cog(SelfBotStatus(bot))
