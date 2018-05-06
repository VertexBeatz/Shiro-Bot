import discord, aiohttp, re
from bs4 import BeautifulSoup as b_s
from io import BytesIO
from discord.ext import commands
from .utils import checks
import os
import random
from random import choice
import lxml    

class Pic:
    def __init__(self, bot):
      self.bot = bot  
    
    @commands.command(name="graff")
    @checks.mod_or_permissions(administrator=True)
    async def graffiti(self, *, content : str):
        """Create a graffiti !"""

        texts = content
        if len(texts) > 14:
          await self.bot.say("14 letters maximum")
        elif any((c in "abcdefghijklmnopqrstuvwxyz") for c in texts.lower()):
          data = dict(
            text = texts,
            font = choice(["whoa", "Searfont", "phillysansps"]),
            texture = choice([1, 2, 3]),
            textcolour = choice(["eeeeee", "ffe26d", "85d860", "69c8eb", "feb6e0"]),
            text_ornament = choice(["none", "clouds", "flowers", "gradient"]),
            bcg = choice(["none", "cloud", "splash", "burst"]),
            bcg_colour = choice(["f9c40b", "369a25", "2356cb", "a227ca", "d92020", "ec6416", "222222"]),
            signature = ""
          )
          await self.bot.type() 
          with aiohttp.ClientSession() as session:
            async with session.post("http://photofunia.com/effects/graffiti_text", data=data) as response:
              if response.status == 200:
                soup = b_s(await response.text(), "lxml")
                download_url = soup.find("div", class_="downloads-container").ul.li.a["href"]
                async with session.get(download_url) as image_response:
                  if image_response.status == 200:
                    image_data = await image_response.read()
                    with BytesIO(image_data) as temp_image:
                      await self.bot.upload(temp_image, filename="graffiti.jpg")
        else:  
          await self.bot.say("Only letters allowed")

    @commands.command(name="retro")
    async def retro(self, *, content : str):
        """Create an image with 3 words seperated with a ; or just with one word"""
        texts = [t.strip() for t in content.split(';')]
        if len(texts) < 3 and not len(texts) > 1:
            lenstr = len(texts[0])
            if lenstr <= 12:
                    data = dict(
                      bcg=choice([1, 2, 3, 4, 5]),
                      txt=choice([1, 2, 3, 4]),
                      text1="",
                      text2=texts[0],
                      text3=""
                    )
                    await self.bot.type() 
                    with aiohttp.ClientSession() as session:
                      async with session.post("http://photofunia.com/effects/retro-wave", data=data) as response:
                        if response.status == 200:
                          soup = b_s(await response.text(), "lxml")
                          download_url = soup.find("div", class_="downloads-container").ul.li.a["href"]
                          async with session.get(download_url) as image_response:
                            if image_response.status == 200:
                              image_data = await image_response.read()
                              with BytesIO(image_data) as temp_image:
                                await self.bot.upload(temp_image, filename="retro.jpg")
            else:
                await self.bot.say("\N{CROSS MARK} Tout many letters on ligne")
                return
        elif len(texts) != 3:
            await self.bot.say("\N{CROSS MARK} Separate your words with a ; or only one word")
            return
        elif len(texts[0]) >= 12:
            await self.bot.say("\N{CROSS MARK} First word too long")
            return
        elif len(texts[1]) >= 12:
            await self.bot.say("\N{CROSS MARK} Second word too long")
            return
        elif len(texts[2]) >= 12:
            await self.bot.say("\N{CROSS MARK} Third word too long")
            return
        else:
            data = dict(
              bcg=choice([1, 2, 3, 4, 5]),
              txt=choice([1, 2, 3, 4]),
              text1=texts[0],
              text2=texts[1],
              text3=texts[2]
            )
            await self.bot.type() 
            with aiohttp.ClientSession() as session:
              async with session.post("http://photofunia.com/effects/retro-wave", data=data) as response:
                if response.status == 200:
                  soup = b_s(await response.text(), "lxml")
                  download_url = soup.find("div", class_="downloads-container").ul.li.a["href"]
                  async with session.get(download_url) as image_response:
                    if image_response.status == 200:
                      image_data = await image_response.read()
                      with BytesIO(image_data) as temp_image:
                        await self.bot.upload(temp_image, filename="retro.jpg")
        
                  
def setup(bot):
  n = Pic(bot)
  bot.add_cog(n)
