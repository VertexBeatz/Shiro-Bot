import discord
from discord.ext import commands
import operator
from datetime import datetime
import calendar

from __main__ import send_cmd_help
from cogs.utils import checks

from .utils.dataIO import dataIO

from time import time
from math import floor
from random import randint

class Level:
    """A cog to create a ranking system!"""

    def __init__(self, bot):
        self.bot = bot
        self.level_path = "data/level/level.json"
        self.path = dataIO.load_json(self.level_path)

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin()
    async def xp(self, ctx):
        await self.bot.say(self.path["guilds"][ctx.message.server.id][ctx.message.author.id]["xp"])
    
    @commands.command(pass_context=True, no_pm=True)
    async def top(self,ctx,top:int=10):
        message= ctx.message
        server = message.server

        if top<1:
            top = 10

        member = {}

        for m in self.path["guilds"][server.id]:
            test= discord.utils.get(server.members, id=m)
            if test:
                member.update({m:self.path["guilds"][server.id][m]["lvl"]})

        all=sorted(member.items(),key=operator.itemgetter(1),reverse=True)

        for y in range(len(all)):
            if message.author.id == all[y][0]:
                g = y

        if len(all) < top:
            top = len(all)
        now = datetime.now()
        b = calendar.monthrange(now.year,now.month)

        start = ""
        em = discord.Embed(title="**Server {}'s leaderboard**\n\n".format(server.name),color=message.author.color)
        if server.icon_url:
            em.set_thumbnail(url=server.icon_url)

        for x in range(top):
            if x+1<10:
                nb = "{} ".format(str(x+1))
            else:
                nb = "{}".format(str(x+1))
            name = discord.utils.get(server.members, id=all[x][0])
            c = "**{}**     {}\n                Lvl:  **{}**      ".format(nb,name.name,all[x][1])
            if x+1 == 1:
                c += ":first_place:"
            if x+1 == 2:
                c += ":second_place:"
            if x+1 == 3:
                c += ":third_place:"
            start += c + "\n"
            if len(start) > 1500:
                if g and g>top:
                    start += "\nYou are number: {}".format(g+1)
                em.description = start
                await self.bot.say(embed=em)
                return
        
        if g and g>top:
            start += "\nYou are number: {}".format(g+1)
        em.description = start
        await self.bot.say(embed=em)

    @commands.command(pass_context=True, no_pm=True)
    async def level(self, ctx, *, user: discord.Member=None):
        """Show a user level"""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author
        
            if user.id not in self.path["guilds"][server.id]:
                curr_time = time()
                exp = floor(randint(5,22)*1.3)
                self.path["guilds"][server.id][user.id] = {}
                self.path["guilds"][server.id][user.id]["xp"] = exp
                self.path["guilds"][server.id][user.id]["time"] = curr_time
                self.path["guilds"][server.id][user.id]["lvl"] = 0
                dataIO.save_json(self.level_path, self.path)
            
            lvl_man = self.path["guilds"][server.id][user.id]["lvl"]
            await self.bot.say("{}, You are level: {}.".format(user.mention, lvl_man))
        else:
            if user.id not in self.path["guilds"][server.id]:
                curr_time = time()
                exp = floor(randint(5,22)*1.3)
                self.path["guilds"][server.id][user.id] = {}
                self.path["guilds"][server.id][user.id]["xp"] = exp
                self.path["guilds"][server.id][user.id]["time"] = curr_time
                self.path["guilds"][server.id][user.id]["lvl"] = 0
                dataIO.save_json(self.level_path, self.path)
            
            lvl_man = int(self.path["guilds"][server.id][user.id]["lvl"])
            await self.bot.say("{}, {} is level: {}.".format(author.mention, user.name, lvl_man))

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin()
    async def defaultchannel(self,ctx, channel: discord.Channel):
        """Set the default channel to send the level up message"""

        message = ctx.message
        server = message.server
        
        self.path["guilds"][server.id]["channels"] = channel.id
        dataIO.save_json(self.level_path, self.path)
        await self.bot.say("Done!")


    @commands.command(pass_context=True, no_pm=True)
    @checks.admin()
    async def userlvl(self, ctx, user: discord.Member=None,*, content:str):
        """Set someone's level

        [p]userlvl @user number"""
        
        message = ctx.message
        server = message.server
        if not user:
            await self.bot.say("I need a user")
            return
        else:
            user = user.id
        try:
            a = int(content)
        except:
            await self.bot.say("This isn't a number :'(")
            return

        b = (5/6)*((2*(a**3))+(27*(a**2))+(91*a))

        if user not in self.path["guilds"][server.id]:
            self.path["guilds"][server.id][user] = {}
            self.path["guilds"][server.id][user]["xp"] = int(b)
            self.path["guilds"][server.id][user]["time"] = 0
            self.path["guilds"][server.id][user]["lvl"] = int(a)
            dataIO.save_json(self.level_path, self.path)
            await self.bot.say("This user hadn't write a message before but I still added him.")
        else:
            self.path["guilds"][server.id][user] = {}
            self.path["guilds"][server.id][user]["xp"] = int(b)
            self.path["guilds"][server.id][user]["time"] = 0
            self.path["guilds"][server.id][user]["lvl"] = int(a)
            dataIO.save_json(self.level_path, self.path)
            await self.bot.say("Done!")

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin()
    async def setxp(self, ctx, user: discord.Member=None,*,content:str):
        """Set someone's xp

        [p]setxp @user number"""

        message = ctx.message
        server = message.server

        if not user:
            await self.bot.say("I need a user")
            return
        else:
            user = user.id
        try:
            b= int(content)
        except:
            await self.bot.say("I can't int this :'(")

        if user not in self.path["guilds"][server.id]:
            await self.bot.say("he has never talk again, let him talk once before!")
            return
        self.path["guilds"][server.id][user]["xp"] = int(b)
        self.path["guilds"][server.id][user]["time"] = 0
        dataIO.save_json(self.level_path, self.path)
        await self.bot.say("Done!")
        

    @commands.command(pass_context=True, no_pm=True)
    @checks.admin()
    async def setlvl(self, ctx, *, content:str):
        """Separate the lvl and the name of the role with a ';'

        Like that: [p]setlvl 25;king"""
        message = ctx.message
        texts = [t.strip() for t in content.split(';')]
        if "Rank" not in self.path["guilds"][message.server.id]:
            self.path["guilds"][message.server.id]["Rank"] = {}
        self.path["guilds"][message.server.id]["Rank"][texts[0]] = texts[1]
        dataIO.save_json(self.level_path, self.path)
        await self.bot.say("Done!")

    async def on_message(self, message):
        if message.server.id == "283534045655334912":
            return
        try:
            if message.author.bot == True:
                return
            if message.server.id not in self.path["guilds"]:
                self.path["guilds"][message.server.id] = {}
                dataIO.save_json(self.level_path, self.path)

            curr_time = time()
            exp = floor(randint(5,22)*1.3)
            try:
                prenium = discord.utils.get(message.server.roles, id="291722698932092928")
                prenium2 = discord.utils.get(message.server.roles, id="291722622935498752")
                for r in message.author.roles:
                    if r.name == prenium.name:
                        exp = exp*2
                    if r.name == prenium2.name:
                        exp = exp*2
            except:
                pass
            

            if message.author.id not in self.path["guilds"][message.server.id]:
                self.path["guilds"][message.server.id][message.author.id] = {}
                self.path["guilds"][message.server.id][message.author.id]["xp"] = exp
                self.path["guilds"][message.server.id][message.author.id]["time"] = curr_time
                self.path["guilds"][message.server.id][message.author.id]["lvl"] = 0
                dataIO.save_json(self.level_path, self.path)
                return
            elif int(curr_time) - int(self.path["guilds"][message.server.id][message.author.id]["time"]) > 60:
                self.path["guilds"][message.server.id][message.author.id]["xp"] += exp
                self.path["guilds"][message.server.id][message.author.id]["time"] = curr_time
                dataIO.save_json(self.level_path, self.path)

            total_xp = int(self.path["guilds"][message.server.id][message.author.id]["xp"])
            n = int(self.path["guilds"][message.server.id][message.author.id]["lvl"])+1
            a = (5/6)*((2*(n**3))+(27*(n**2))+(91*n))

            if total_xp > a:
                self.path["guilds"][message.server.id][message.author.id]["lvl"] = n
                dataIO.save_json(self.level_path, self.path)
                if "channels" in self.path["guilds"][message.server.id]:
                    yolo = self.path["guilds"][message.server.id]["channels"]
                    yolo = message.server.get_channel(yolo)
                else:
                    yolo = message.channel
                await self.bot.send_message(yolo, "{}, You are now level {}!".format(message.author.mention, n))

                cur = str(self.path["guilds"][message.server.id][message.author.id]["lvl"])
                if cur in self.path["guilds"][message.server.id]["Rank"]:
                    role = discord.utils.get(message.server.roles, name=self.path["guilds"][message.server.id]["Rank"][cur])
                    for r in message.author.roles:
                        if r.name == role.name:
                            return
                    try:
                        await self.bot.add_roles(message.author, role)
                        if "channels" in self.path["guilds"][message.server.id]:
                            yolo = self.path["guilds"][message.server.id]["channels"]
                            yolo = message.server.get_channel(yolo)
                        else:
                            yolo = message.channel
                        await self.bot.send_message(yolo, "{}, You gained the role: {}".format(message.author.mention, role.name))
                    except:
                        pass
        except:
            pass

    """async def _on_voice_state_update(self, before, after):
        if after.server.id == "283534045655334912":
            return
        try:
            server = after.server
            if server.id in self.path["guilds"]:
                if after.voice_channel and not after.self_deaf:
                    self.path["guilds"][server.id][after.id]["join"] = time()
                if after.voice_channel is None or after.self_deaf:
                    total = time() - self.path["guilds"][server.id][after.id]["join"]
                    total = int(int(total)/60)
                    exp = floor(randint(5,22)*1.3)*total
                    try:
                        prenium = discord.utils.get(server.roles, id="291722698932092928")
                        prenium2 = discord.utils.get(server.roles, id="291722622935498752")
                        for r in after.roles:
                            if r.name == prenium.name:
                                exp = exp*2
                            if r.name == prenium2.name:
                                exp = exp*2
                    except:
                        pass
                    self.path["guilds"][server.id][after.id]["xp"] += exp
                    dataIO.save_json(self.level_path, self.path)
                    

                    total_xp = int(self.path["guilds"][server.id][after.id]["xp"])
                    n = int(self.path["guilds"][server.id][after.id]["lvl"])+1
                    a = (5/6)*((2*(n**3))+(27*(n**2))+(91*n))

                    if total_xp > a:
                        self.path["guilds"][server.id][after.id]["lvl"] = n
                        dataIO.save_json(self.level_path, self.path)
                        if "channels" in self.path["guilds"][server.id]:
                            yolo = self.path["guilds"][server.id]["channels"]
                            yolo = server.get_channel(yolo)
                            await self.bot.send_message(yolo, "{}, You are now level {}!".format(after.mention, n))

                        cur = str(self.path["guilds"][server.id][after.id]["lvl"])
                        if cur in self.path["guilds"][server.id]["Rank"]:
                            role = discord.utils.get(server.roles, name=self.path["guilds"][server.id]["Rank"][cur])
                            for r in after.roles:
                                if r.name == role.name:
                                    return
                            try:
                                await self.bot.add_roles(after, role)
                                if "channels" in self.path["guilds"][server.id]:
                                    yolo = self.path["guilds"][server.id]["channels"]
                                    yolo = server.get_channel(yolo)
                                    await self.bot.send_message(yolo, "{}, You gained the role: {}".format(after.mention, role.name))
                            except:
                                print("fin")
                                pass

                    
        except Exception as e:
            print('Houston, we have a problem: {}'.format(e))"""


def setup(bot):
    n = Level(bot)
    bot.add_cog(n)
