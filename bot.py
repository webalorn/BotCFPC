import discord

client = discord.Client()

chandata = None
data = {}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await regenData()

async def regenData():
    global chandata
    if chandata is None:
        for i in client.get_all_channels():
            if i.name == "data":
                chandata = i
                break
    async for message in chandata.history():
        con = message.content.split(" ")
        idx = (await getUser(message)).id
        if not (idx in data.keys()):
            data[idx] = {}
        if con[0] == "franceioi":
            data[idx]["franceioi"] = con[2]
        if con[0] == "codeforces":
            data[idx]["codeforces"] = con[2]

async def getUser(message):
    args = message.content.split(" ")[1:]
    member = None

    for i in client.get_all_members():
        if i.mentioned_in(message) or i.display_name in args or i.name in args:
            if member:
                await message.channel.send("Echec - Plusieurs membres ont été reconnus")
            member = i
    if not member:
        await message.channel.send("Echec - Aucun membre n'a été reconnu")
    return member

async def cmdSendInfo(message):
    args = message.content.split(" ")[1:]
    member = await getUser(message)
    if member:
        idx = member.id
        if not (idx in data.keys()):
            await message.channel.send("Je ne sais rien sur ce membre")
            return
        info = data[idx]
        msg = ""
        if ("franceioi" in info):
            msg += "http://www.france-ioi.org/user/perso.php?sLogin="+data[idx]["franceioi"]
        if ("codeforces" in info):
            if msg:
                msg += "\n"
            msg += "http://codeforces.com/profile/"+data[idx]["codeforces"]
        await message.channel.send(msg)

async def cmdLinkUser(message):
    if not message.author.permissions_in(message.channel).administrator:
        await message.channel.send("(!) Action interdite")
        return
    args = message.content.split(" ")[1:]
    member = await getUser(message)
    if member:
        await chandata.send("%s %s %s"%(args[0], member.mention, args[2]))
        if not member.id in data:
            data[member.id] = {}
        data[member.id][args[0]] = args[2]
    await message.channel.send("Lien créé avec succès")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('&hello'):
        await message.channel.send("Bonjour {} !".format(message.author.display_name))

    if message.content.startswith("&info"):
        await cmdSendInfo(message)

    if message.content.startswith("&regen"):
        await regenData()
        await message.channel.send("Les informations ont été actualisées")

    if message.content.startswith("&link"):
        await cmdLinkUser(message)

token = ""
with open("token", "r") as f:
    token = f.read()

client.run(token)