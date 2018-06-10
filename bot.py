import discord
from discord.ext import commands

prefix = "&"
bot = commands.Bot(command_prefix=prefix)

token = ""
with open("token", "r") as f:
    token = f.read()

bot.run(token)