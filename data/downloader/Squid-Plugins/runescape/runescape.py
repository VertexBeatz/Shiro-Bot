from discord.ext import commands
import aiohttp
from cogs.utils.chat_formatting import *
import fractions

try:
    import feedparser
except:
    feedparser = None


class Runescape:
    """Runescape stuff"""

    def __init__(self, bot):
        self.bot = bot
        self.base_url = \
            "http://services.runescape.com/m=hiscore/index_lite.ws?player="
        self.alog_url = \
            ("http://services.runescape.com/m=adventurers-log/rssfeed?"
             "searchName=")
        self.max_level = 120
        self.skill_list = [
            "Overall",
            "Attack",
            "Defence",
            "Strength",
            "Constitution",
            "Ranged",
            "Prayer",
            "Magic",
            "Cooking",
            "Woodcutting",
            "Fletching",
            "Fishing",
            "Firemaking",
            "Crafting",
            "Smithing",
            "Mining",
            "Herblore",
            "Agility",
            "Thieving",
            "Slayer",
            "Farming",
            "Runecrafting",
            "Hunter",
            "Construction",
            "Summoning",
            "Dungeoneering",
            "Divination",
            "Invention"
        ]
        self.elite_skills = [27, ]
        self.skill_levels = self._skill_levels()
        self.elite_levels = [0.4796 * pow(x, 4) - 12.788 * pow(x, 3) + 228.56 *
                             pow(x, 2) + 2790.8 * x - 31674
                             for x in range(1, 150)]

    def _skill_levels(self):
        xplist = []

        points = 0
        for level in range(1, self.max_level):
            points += int(level + 300 * pow(2, level / 7))
            xplist.append(int(points / 4))

        return xplist

    def _get_level(self, exp):
        exp = int(exp)
        for level, currExp in enumerate(self.skill_levels):
            if currExp > exp:
                return str(level + 1)
        return '120'

    def _get_elite_level(self, exp):
        exp = int(exp)
        for level, currExp in enumerate(self.elite_levels):
            if currExp > exp:
                return str(level + 1)
        return '150'

    def _commafy(self, num):
        try:
            int(num)
        except:
            return num
        else:
            return "{:,}".format(int(num))

    def _fmt_hs(self, data):
        ret = "```"
        retlist = [['Skill', 'Rank', 'Level', 'Experience']]
        for i in range(len(data)):
            if i < len(self.skill_list):
                splitted = data[i].split(',')
                if i != 0:
                    if i in self.elite_skills:
                        splitted[1] = self._get_elite_level(splitted[2])
                    else:
                        splitted[1] = self._get_level(splitted[2])
                splitted[0] = self._commafy(splitted[0])
                splitted[1] = self._commafy(splitted[1])
                splitted[2] = self._commafy(splitted[2])
                retlist.append([self.skill_list[i]] + splitted)
        col_width = max(len(word) for row in retlist for word in row) + 2
        for row in retlist:
            ret += "".join(word.ljust(col_width) for word in row) + "\n"
        ret += "```"
        return ret

    def _fmt_alog(self, username, titles):
        ret = "```Recent Adventure Log for " + username + ":\n"
        for title in titles:
            ret += "\t" + title + "\n"
        ret += "```"
        return ret

    @commands.command(no_pm=True)
    async def alog(self, *, username):
        """Gets a users recent adventure log"""
        username = username.replace(" ", "_")
        if feedparser is None:
            await self.bot.say("You'll need to run `pip3 install feedparser` "
                               "before you can get a user's adventure log.")
            return
        url = self.alog_url + username
        try:
            page = await aiohttp.get(url)
            text = await page.text()
            text = text.replace("\r", "")
        except:
            await self.bot.say("No user found.")

        feed = feedparser.parse(text)
        titles = [post.title for post in feed.entries]

        await self.bot.say(self._fmt_alog(username, titles))

    @commands.command(no_pm=True)
    async def hs(self, *, username):
        """Gets hiscores info"""
        username = username.replace(" ", "_")
        url = self.base_url + username
        try:
            page = await aiohttp.get(url)
            text = await page.text()
            text = text.replace("\r", "")
            text = text.split("\n")
        except:
            await self.bot.say("No user found.")
        else:
            await self.bot.say(self._fmt_hs(text))

    @commands.command()
    async def dropcalc(self, drop_rate, threshold, kill_count):
        """Calculates your chances of (not) getting a drop."""
        try:
            drop_rate = float(fractions.Fraction(drop_rate))
            threshold = int(threshold)
            kill_count = int(kill_count)
        except:
            await self.bot.say("All arguments must be numbers.")
            return
        if drop_rate > 1:
            drop_rate = 1 / drop_rate

        if drop_rate < 0 or threshold < 0 or kill_count < 0:
            await self.bot.say("All values must be above 0.")
            return

        if threshold == 0 or kill_count < threshold:
            chance_to_notget = (1 - drop_rate)**(kill_count)
        else:
            chance_to_notget = 1
            threshold_crosses = kill_count // threshold
            threshold_crosses = threshold_crosses if threshold_crosses <= 9 \
                else 9
            for i in range(0, threshold_crosses):
                mult = 1 + i
                chance_to_notget *= (1 - drop_rate * mult)**(mult * threshold)

        chance_to_get = 1 - chance_to_notget
        msg = ("Your chance of getting that drop in {}".format(kill_count) +
               " kills is {:.3f}%".format(chance_to_get * 100))
        await self.bot.say(msg)


def setup(bot):
    n = Runescape(bot)
    bot.add_cog(n)
