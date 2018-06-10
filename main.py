from bot import bot
import misc

token = ""
with open("token", "r") as f:
    token = f.read()

bot.run(token)