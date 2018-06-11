import discord, aiohttp, time, json, asyncio

before_contest = sorted([60*10, 60*60*2, 60*60*24])
codeforces_notif_waiting_delay = 3*60
config_file = 'config.json'
channel_alerts_id = '450184920489263107'#'432540436582760473'
config = {}

client = discord.Client()

chandata = None
data = {}

def save_config():
    with open(config_file, 'w') as f:
        json.dump(config, f)

async def getJsonOf(*p, **pn):
    async with aiohttp.get(*p, **pn) as r:
        if r.status == 200:
            return await r.json()

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

async def background_tasks_codeforces():
    await client.wait_until_ready()
    while not client.is_closed:
        content = None
        try:
            content = await getJsonOf('http://codeforces.com/api/contest.list')
        except Exception as e:
            print('Codeforces API call error:', e)
            continue

        nextContests = [contest for contest in content['result'] if contest['phase'] == "BEFORE"]

        channel = None


        for server in client.servers:
            for chan in server.channels:
                if chan.id == channel_alerts_id:
                    channel = chan
        if chan:
            channelCfg = config['contests']

            notifyContests = []

            for contest in nextContests:
                contestId = str(contest['id'])
                for delay in before_contest:
                    if contest['relativeTimeSeconds'] >= -delay and (not contestId in channelCfg or channelCfg[contestId] > delay):
                        channelCfg[contestId] = delay
                        notifyContests.append(contest)

            for contest in notifyContests:
                seconds = -1*contest['relativeTimeSeconds']
                duree = time.strftime(
                    ('%-M minutes %-S seconds' if seconds < 60*60 else '%-Hh %-M min') if seconds < 60*60*24 else '%-d jours %-Hh %-M min',
                    time.gmtime(seconds)
                )
                msg = '@everyone: {0} dans {1}'.format(contest['name'], duree)
                if seconds < 60*60*24 and seconds > 5*60:
                    msg += ' [register at: http://codeforces.com/contestRegistration/{0}]'.format(contest['id'])
                await client.send_message(channel, msg)
            save_config()
        await asyncio.sleep(codeforces_notif_waiting_delay)

token = ""
with open("token", "r") as f:
    token = f.read()

try:
    with open(config_file) as f:
        config = json.load(f)
except:
    config = {}
finally:
    for dict_key in ['contests']:
        if not dict_key in config:
            config[dict_key] = {}

client.loop.create_task(background_tasks_codeforces())
client.run(token)