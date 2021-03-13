import sys
import discord
import requests
import json
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import aiohttp
import asyncio
import paramiko
import os

# import subprocess

bot = commands.Bot(command_prefix="]", intents=discord.Intents.all(), chunk_guilds_at_startup=True,
                   case_insensitive=True)
load_dotenv()

token = os.getenv('token')
crabwings_role_id = int(os.getenv('crabwings_role_id'))
elktail_role_id = int(os.getenv('elktail_role_id'))
frogface_role_id = int(os.getenv('frogface_role_id'))
goosegills_role_id = int(os.getenv('goosegills_role_id'))
hippohips_role_id = int(os.getenv('hippohips_role_id'))
client_role_id = int(os.getenv('client_role_id'))
subuser_role_id = int(os.getenv('subuser_role_id'))
verified_role_id = int(os.getenv('verified_role_id'))
guild_id = int(os.getenv('guild_id'))
verification_channel = int(os.getenv('verification_channel'))
verification_message = int(os.getenv('verification_message'))
application_api_key = os.getenv('application_api_key')
running_on_panel = str(os.getenv('running_on_panel'))
crabwings_ip = os.getenv('crabwings_ip')
crabwings_port = int(os.getenv('crabwings_port'))
crabwings_username = os.getenv('crabwings_username')
crabwings_password = os.getenv('crabwings_password')

if running_on_panel == "False":
    running_on_panel = False
else:
    running_on_panel = True

logging.basicConfig(filename='console.log',
                    level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


@bot.event
async def on_ready():
    # Marks bot as running
    logging.info('I am running.')
    servers = bot.guilds
    logging.info("I am in the following " + str(len(servers)) + " servers:")
    global number_servers
    number_servers = 0
    for server in servers:
        print(server.name + " by " + server.owner.name + "#" + server.owner.discriminator)
        number_servers+=1

@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    if running_on_panel:
        global verification_message
        global verification_channel
        if payload.message_id != verification_message:
            return
        if payload.user_id == bot.user.id:
            return
        # Remove the reaction
        guild = discord.utils.get(bot.guilds, id=guild_id)
        verification_channel_obj = await bot.fetch_channel(verification_channel)
        verification_message_obj = await verification_channel_obj.fetch_message(verification_message)
        member = guild.get_member(payload.user_id)
        await verification_message_obj.remove_reaction(payload.emoji, member)
        if str(payload.emoji) == "✅":
            await member.send(
                "Hey there! It looks like you'd like to verify your account. I'm here to help you with that!\n\nIf you're confused at any point, see https://birdflop.com/verification for a tutorial.\n\nWith that said, let's get started! You'll want to start by grabbing some API credentials for your account by signing into https://panel.birdflop.com. Head over to the **Account** section in the top right, then click on the **API Credentials tab**. You'll want to create an API key with description `Verification` and `172.18.0.2` in the **Allowed IPs section**.\n\nWhen you finish entering the necessary information, hit the blue **Create **button.\n\nNext, you'll want to copy your API credentials. After clicking **Create**, you'll receive a long string. Copy it with `ctrl+c` (`cmnd+c` on Mac) or by right-clicking it and selecting **Copy**.\n\nIf you click on the **Close **button before copying the API key, no worries! Delete your API key and create a new one with the same information.\n\nFinally, direct message your API key to Botflop: that's me!\n\nTo verify that you are messaging the key to the correct user, please ensure that the my ID is `Botflop#5807` and that my username is marked with a blue **BOT** badge. Additionally, the only server under the **Mutual Servers** tab should be Birdflop Hosting.\n\nAfter messaging me your API key, you should receive a success message. If you do not receive a success message, please create a ticket in the <#764280387253305354> channel.")
            logging.info("sent verification challenge to " + member.name + "#" + str(member.discriminator) + " (" + str(
                member.id) + ")")
        else:
            file = open('users.json', 'r')
            data = json.load(file)
            file.close()
            i = 0
            j = -1
            for client in data['users']:
                j += 1
                if client['discord_id'] == member.id:
                    data['users'].pop(j)
                    i = 1
            if i == 1:
                json_dumps = json.dumps(data, indent=2)
                file = open('users.json', 'w')
                file.write(json_dumps)
                file.close()
                await member.edit(roles=[])
                await member.send("Your Discord account has successfully been unlinked from your Panel account!")
                logging.info(
                    'successfully unlinked ' + member.name + "#" + str(member.discriminator) + " (" + str(
                        member.id) + ")")


@bot.command()
async def ping(ctx):
    if running_on_panel:
        if guild_id == ctx.guild.id:
            await ctx.send(f'Panel bot ping is {round(bot.latency * 1000)}ms')
    if not running_on_panel:
        await ctx.send(f'Public bot ping is {round(bot.latency * 1000)}ms')


@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    if not running_on_panel:
        channel = await bot.fetch_channel(int(url.split("/")[5]))
        message = await channel.fetch_message(int(url.split("/")[6]))
        await message.add_reaction(reaction)
        logging.info('reacted to ' + url + ' with ' + reaction)

@bot.command(name="servers", pass_context=True)
async def servers(ctx, user_discord_id_var: discord.Member=None):
    linked = False
    support_role = discord.utils.get(ctx.guild.roles, id = 816211260475179008)
    if not support_role in ctx.author.roles:
        if not user_discord_id_var:
            user_discord_id = ctx.author.id
        else:
            await ctx.send("Sorry, you can only check your own servers. Please use the `]servers` command.")
            return
    else:
        if not user_discord_id_var:
            user_discord_id = ctx.author.id
        else:
        	user_discord_id = user_discord_id_var.id
    with open("users.json", "r") as file:
        data = json.load(file)
        for user in data["users"]:
            if user['discord_id'] == int(user_discord_id):
                linked = True
                client_api_key = user['client_api_key']
                url = "https://panel.birdflop.com/api/client"

                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + client_api_key,
                }

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        # If API token is verified to be correct:
                        if response.status == 200:
                            # Formats response of account in JSON format
                            json_response = await response.json()
                            embed_var = discord.Embed(title="Servers", color=0x1D83D4)
                            for server in json_response['data']:
                                if server['attributes']['server_owner'] == True:
                                    server_owner = "Owner"
                                elif server['attributes']['server_owner'] == False:
                                    server_owner = "Subuser"
                                serverid = server['attributes']['uuid']
                                serverid = serverid.split("-")[0]
                                embed_var.add_field(name=server['attributes']['name'], 
                                                    value=f"ID: [{serverid}](https://panel.birdflop.com/server/{serverid})\nRole: {server_owner}\nNode: {server['attributes']['node']}", inline=True)
                            await ctx.send(embed=embed_var)
        if not linked:
            await ctx.send("You must verify your account to use this command. You can verify your account by reacting in <#790217956738334760>")
                

@tasks.loop(minutes=10)
async def updater():
    # Update backups
    logging.info('Ensuring backups')
    url = "https://panel.birdflop.com/api/application/servers"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + application_api_key,
    }
    # response = requests.get(url, headers=headers)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            servers_json_response = await response.json()

            file = open('modified_servers.json', 'r')
            modified_servers = json.load(file)
            file.close()

            i = -1

            for server in servers_json_response['data']:
                i += 1
                already_exists = False
                for server2 in modified_servers['servers']:
                    if not already_exists:
                        if server['attributes']['uuid'] == server2['uuid']:
                            already_exists = True
                if not already_exists:
                    headers = {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + application_api_key,
                    }

                    data = '{ "allocation": ' + str(server['attributes']['allocation']) + ', "memory": ' + str(
                        server['attributes']['limits']['memory']) + ', "swap": 4000, "disk": ' + str(
                        server['attributes']['limits']['disk']) + ', "io": ' + str(
                        server['attributes']['limits']['io']) + ', "cpu": ' + str(
                        server['attributes']['limits'][
                            'cpu']) + ', "threads": null, "feature_limits": { "databases": ' + str(
                        server['attributes']['feature_limits']['databases']) + ', "allocations": ' + str(
                        server['attributes']['feature_limits']['allocations']) + ', "backups": 3 } }'

                    async with aiohttp.ClientSession() as session:
                        async with session.patch('https://panel.birdflop.com/api/application/servers/' + str(
                                server['attributes']['id']) + '/build', headers=headers, data=data) as response:
                            if response.status == 200:
                                modified_servers['servers'].append({
                                    'uuid': str(server['attributes']['uuid'])
                                })

                                file = open('modified_servers.json', 'w')
                                json_dumps = json.dumps(modified_servers, indent=2)
                                file.write(json_dumps)
                                file.close()

                                logging.info("modified " + str(server['attributes']['name']) + ' with data ' + data)
                            else:
                                logging.info(
                                    "failed to modify " + str(server['attributes']['name']) + ' with data ' + data)


# Plugin Updater
# @bot.command()
# async def update(ctx, server, plugin):
#    command_discord_id = ctx.message.author.id
#    await ctx.send (f'your discord ID is {command_discord_id}')
#    file = open('users.json', 'r')
#    data = json.load(file)
#    file.close()
#    i=-1
#    for client in data['users']:
#        if i==-1:
#            if client["discord_id"] == command_discord_id:
#                i=0
#                command_client_id = client["client_id"]
#                command_client_api_key = client["client_api_key"]
#    if i==-1:
#        await ctx.send("You must be verified to use this command.")
#    else:
#        if plugin.lower() == "votingplugin":
#            subprocess.call(['java', '-jar', 'spiget-downloader.jar', '--url', 'https://www.spigotmc.org/resources/votingplugin.15358/download?version=373388', '--file', 'ProtocolLib.jar'])

#
#            print("Finding latest VotingPlugin")
#
#            headers = {
#              "cache-control": "max-age=1800",
#              "content-type": "application/json; charset=utf-8"
#            }
#
#            response = requests.get("https://api.spiget.org/v2/resources/15358/versions/latest")
#            spiget_json = response.json()
#            print("Latest Version = " + str(spiget_json["id"]))
#
#            url = "https://www.spigotmc.org/resources/votingplugin.15358/download?version=373388"
#            headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
#            r = requests.get(url, headers=headers)
#            open('VotingPlugin1.jar', 'wb').write(r.content)
#
#
#            #urllib.request.urlretrieve("https://api.spiget.org/v2/resources/15358/versions/373388/download",'/home/container/zzzcache/VotingPlugin1.jar')
#            #urllib.request.urlretrieve("https://www.spigotmc.org/resources/votingplugin.15358/download?version=373388",'/home/container/zzzcache/VotingPlugin2.jar')
#
#
#
#            headers = {
#                'Accept': 'application/json',
#                'Content-Type': 'application/json',
#                'Authorization': 'Bearer ' + command_client_api_key,
#            }
#
#            response = requests.get(f'https://panel.birdflop.com/api/client/servers/{server}/files/upload', headers=headers)
#            print(str(response))
#            update_json = response.json()
#            transfer_url = update_json["attributes"]["url"]
#            print(transfer_url)
#        else:
#            await ctx.send("Sorry, that is not a valid plugin.")

@updater.before_loop
async def before_updater():
    await bot.wait_until_ready()


if running_on_panel:
    for file_name in os.listdir('./cogs'):
        if file_name.endswith('_panel.py'):
            bot.load_extension(f'cogs.{file_name[:-3]}')
else:
    for file_name in os.listdir('./cogs'):
        if file_name.endswith('_public.py'):
            bot.load_extension(f'cogs.{file_name[:-3]}')

if running_on_panel:
    print("running on panel, starting loops")
    updater.start()
    linking_updater = bot.get_cog('Linking_updater')
    linking_updater.linking_updater.start()

bot.run(token)

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
