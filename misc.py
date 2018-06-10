from bot import bot

@bot.event
async def on_ready():
    print('Connecté')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def ping(ctx):
    '''
    Retourne la latence du bot
    '''

    latency = bot.latency
    await ctx.send(latency)