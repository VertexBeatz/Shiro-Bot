import discord
from discord.ext import commands
import aiohttp
import praw
import pytz
import logging
import random
import os
import time
import asyncio
import datetime

logging.basicConfig(level=logging.ERROR)
reddit = praw.Reddit(client_id='EDR6GfMSuhGxcQ',
                     client_secret='z7XjPOr4QUyXgvyOZw4fFSP4CWk',
                     user_agent='DiscordSalty')

class Fun:
    """Ce cog permet des trucs inutiles!"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def c4(self, ctx):
        """Start a connect 4
        
        You need to tag someone to play"""
        message = ctx.message

        def check_win(board):
            for a in range(6):
                for b in range(4):
                    if board[a][b] == board[a][b+1] == board[a][b+2] == board[a][b+3] != 0: # ->
                        return board[a][b]

            for a in range(3):
                for b in range(7):
                    if board[a][b] == board[a+1][b] == board[a+2][b] == board[a+3][b] != 0: # |v
                        return board[a][b]

            for a in range(3):
                for b in range(4):
                    if board[a][b] == board[a+1][b+1] == board[a+2][b+2] == board[a+3][b+3] != 0: # Vers bas droite
                        return board[a][b]

            for a in range(3, 6):
                for b in range(3, 7):
                    if board[a][b] == board[a-1][b-1] == board[a-2][b-2] == board[a-3][b-3] != 0: # Vers haut gauche
                        return board[a][b]

            for a in range(3, 6):
                for b in range(4):
                    if board[a][b] == board[a-1][b+1] == board[a-2][b+2] == board[a-3][b+3] != 0: # Vers haut droite
                        return board[a][b]

            for a in range(3):
                for b in range(3, 7):
                    if board[a][b] == board[a-1][b-1] == board[a-2][b-2] == board[a-3][b-3] != 0: # Vers bas gauche
                        return board[a][b]
            nul = 1
            for i in board:
                for j in i:
                    if j == 0:
                        nul = 0

            if nul == 1:
                return -1

            return 0

        def add_token(board, player, column):
            for i in range(len(board)):
                if board[i][column] != 0:
                    if i == 0:
                        break
                    else:
                        board[i-1][column] = player
                        break

            if board[5][column] == 0:
                board[5][column] = player

            return board

        async def player_turn(board, player, playernum):
            col = -1
            muh = -1
            while muh == -1:
                muh = 0
                col = await self.bot.wait_for_message(timeout = 60, author = player)

                if col == None:
                    return None
                if col.content == ".GG":
                    return 1 if playernum == 2 else 2

                for i in col.content:
                    if i not in "1234567":
                        muh = -1
                if muh != -1:
                    col = int(col.content)
                    if col < 0 or col > 8:
                        muh = -1
            col -= 1
            add_token(board, playernum, col)
            return board

        def print_board(board, player, tour):
            start = ""
            for i in board:
                print("|", end = "")
                for j in i:
                    if j == 1:
                        start += ":large_blue_circle:"
                    elif j == 2:
                        start += ":red_circle:"
                    else:
                        start += ":white_circle:"
                start += "\n"
            start = start[:-1]
            jeton = ":large_blue_circle:" if tour%2 == 1 else ":red_circle:"
            start += " Turn {} | {} {}".format(tour, jeton, player.name)
            return start        

        if len(message.mentions) == 0:
            await self.bot.say("{} You need to mention someone to play.".format(message.author.mention))
            return
        if message.author in message.mentions:
            await self.bot.say("{0} want to play against {0} :')".format(message.author.mention))
            return
        
        board = [[0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0]]
        player1 = message.author
        player2 = message.mentions[0]
        await self.bot.say(":large_blue_circle: {} vs :red_circle: {}\nTime per turn: 60 seconds.".format(player1.mention, player2.mention))

        winner = 0
        turn = 0
        last = await self.bot.say(print_board(board, player1, turn+1))
        while winner == 0:
            turn += 1
            # turn % 2 == 1 -> J1
            # turn % 2 == 0 -> J2
            player = player1 if turn%2 == 1 else player2
            otherplayer = player2 if player == player1 else player1
            playernum = 1 if turn%2 == 1 else 2
            board = await player_turn(board, player, playernum)
            if board == None:
                await self.bot.say("Time's up! Game canceled.")
                return
            elif board == 1:
                winner = 1
                continue
            elif board == 2:
                winner = 2
                continue
            
            await self.bot.delete_message(last)
            last = await self.bot.say(print_board(board, otherplayer, turn+1))
            winner = check_win(board)
        if winner == 1:
            await self.bot.say(":large_blue_circle: {} won!".format(player1.mention))
        elif winner == 2:
            await self.bot.say(":red_circle: {} won!".format(player2.mention))
        elif winner == -1:
            await self.bot.say("Draw !")



    @commands.command(pass_context=True)
    async def ttt(self, ctx):
        """Start a tic tac toe!
        
        You need to tag someone to play !"""
        message = ctx.message

        def check_win(board, case):
            if case != 0 and type(case) == int:
                return case + 1
            for a in range(2):
                b = 0
                if board[a][b] == board[a][b+1] == board[a][b+2] != 0:
                    return board[a][b]
            
            a = 0
            for b in range(2):
                if board[a][b] == board[a+1][b] == board[a+2][b] != 0: # |v
                    return board[a][b]

            a = 0
            b = 0
            if board[a][b] == board[a+1][b+1] == board[a+2][b+2] != 0: # Vers bas droite
                return board[a][b]

            a = 2
            b = 0
            if board[a][b] == board[a-1][b+1] == board[a-2][b+2] != 0: # Vers bas gauche
                return board[a][b]

            nul = 1
            for i in board:
                for j in i:
                    if j == 0:
                        nul = 0

            if nul == 1:
                return -1

            return 0

        def add_token(board, player, column, ligne):
            if board[ligne][column] == 0:
                board[ligne][column] = player
                case = False
            else:
                case = player

            return board, case

        async def player_turn(board, player, playernum):
            col = -1
            muh = -1
            case = playernum
            while muh == -1:
                muh = 0
                col = await self.bot.wait_for_message(timeout = 60, author = player)

                if col is None:
                    return None, ""
                if col.content == "..GG":
                    return 1 if playernum == 2 else 2
                if len(col.content) != 2:
                    muh = -1
                for i in col.content:
                    if i.lower() not in "123abc":
                        muh = -1
                if muh != -1:
                    lig = int(ord(col.content[:1].lower()) - 96)
                    col = int(col.content[1:])
                    if col < 0 or col > 3:
                        muh = -1
            col -= 1
            lig -= 1
            board, case = add_token(board, playernum, col, lig)
            return board, case

        def print_board(board, player, tour):
            start = ""
            for i in board:
                for j in i:
                    if j == 1:
                        start += ":white_check_mark:"
                    elif j == 2:
                        start += ":negative_squared_cross_mark:"
                    else:
                        start += ":black_large_square:"
                    start += " "
                start += "\n"
            start = start[:-1]
            jeton = ":white_check_mark:" if tour%2 == 1 else ":negative_squared_cross_mark:"
            start += " Turn {} | {} {}".format(tour, jeton, player.name)
            return start        

        if len(message.mentions) == 0:
            await self.bot.say("{} You need to mention someone to play.".format(message.author.mention))
            return
        if message.author in message.mentions:
            await self.bot.say("{0} want to play against {0} :')".format(message.author.mention))
            return
        
        board = [[0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]]

        player1 = message.author
        player2 = message.mentions[0]
        await self.bot.say(":white_check_mark: {} vs :negative_squared_cross_mark: {}\nTime per turn: 60 seconds.".format(player1.mention, player2.mention))

        winner = 0
        turn = 0
        last = await self.bot.say(print_board(board, player1, turn+1))
        while winner == 0:
            turn += 1
            # turn % 2 == 1 -> J1
            # turn % 2 == 0 -> J2
            player = player1 if turn%2 == 1 else player2
            otherplayer = player2 if player == player1 else player1
            playernum = 1 if turn%2 == 1 else 2
            board, case = await player_turn(board, player, playernum)
            if case == playernum:
                await self.bot.say("{}, already chosen !".format(player.mention))
                asyncio.sleep(0.2)
                await self.bot.say("{} won !".format(otherplayer.mention))
                return
            if board is None:
                await self.bot.say("Time's up ! Game canceled.")
                return
            elif board == 1:
                winner = 1
                continue
            elif board == 2:
                winner = 2
                continue

            await self.bot.delete_message(last)
            last = await self.bot.say(print_board(board, otherplayer, turn+1))
            winner = check_win(board, case)
        if winner == 1:
            await self.bot.say(":white_check_mark: {} won !".format(player1.mention))
        elif winner == 2:
            await self.bot.say(":negative_squared_cross_mark: {} won !".format(player2.mention))
        elif winner == -1:
            await self.bot.say("Match nul !")

    @commands.command(pass_context=True)
    async def cat(self):
        """Show a cat !"""

        url = 'http://aws.random.cat/meow'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                swag = await resp.json()
                swag = swag['file']
                await self.bot.say(swag)

    @commands.command(pass_context=True)
    async def dog(self):
        """Show a dog !"""

        url = 'https://dog.ceo/api/breeds/image/random'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                sswag = await resp.json()
                sswag = sswag['message']
                await self.bot.say(sswag)


    @commands.command()
    async def food(self):
        """FOOD !"""

        submission = reddit.subreddit('FoodPorn').random()
        text = submission.url
        await self.bot.say(text)


def setup(bot):
    bot.add_cog(Fun(bot))