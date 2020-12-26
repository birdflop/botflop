import os
import discord
import requests
import json
import asyncio
import aiohttp
import logging
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv

bot = commands.Bot(command_prefix = ".", intents=discord.Intents.all(), chunk_guilds_at_startup=True)

load_dotenv()
token = os.getenv('token')
crabwings_role_id = int(os.getenv('crabwings_role_id'))
duckfeet_role_id = int(os.getenv('duckfeet_role_id'))
client_role_id = int(os.getenv('client_role_id'))
subuser_role_id = int(os.getenv('subuser_role_id'))
verified_role_id = int(os.getenv('verified_role_id'))
guild_id = int(os.getenv('guild_id'))
verification_channel = int(os.getenv('verification_channel'))
verification_message = int(os.getenv('verification_message'))

@bot.event
async def on_ready():
    # Marks bot as running
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    logging.info('I am running yay')
    print('I am running.')
    
@bot.event
async def on_message(message):
    if message.author != bot.user and message.guild == None:
        channel = message.channel
        # Potential API key, so tries it out
        if len(message.content) == 48:
            url = "https://panel.birdflop.com/api/client/account"

            cookies = {
                'pterodactyl_session': 'eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%3D%3D',
            }

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + message.content,
            }

            response = requests.get(url, headers=headers, cookies=cookies)

            # If API token is verified to be correct:
            if str(response) == "<Response [200]>":

                # Formats response of account in JSON format
                json_response = response.json()

                
                # Loads contents of users.json
                file = open('users.json', 'r')
                data = json.load(file)
                file.close()

                # Checks if user exists. If so, skips adding them to users.json
                client_id_already_exists = False
                discord_id_already_exists = False
                for user in data['users']:
                    if user['client_id'] == json_response['attributes']['id']:
                        client_id_already_exists = True
                        print("User already exists")
                    if user['discord_id'] == message.author.id:
                        discord_id_already_exists = True
                        print("User already exists")
                if client_id_already_exists == False and discord_id_already_exists == False:       
                    data['users'].append({
                        'discord_id': message.author.id,
                        'client_id': json_response['attributes']['id'],
                        'client_api_key': message.content
                    })
                    json_dumps = json.dumps(data, indent = 2)
                    # Adds user to users.json
                    file = open('users.json', 'w')
                    file.write(json_dumps)
                    file.close()
                    
                    guild = bot.get_guild(guild_id)
                    member = guild.get_member(message.author.id)
                    if member:

                        url = "https://panel.birdflop.com/api/client"

                        cookies = {
                            'pterodactyl_session': 'eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%3D%3D',
                        }

                        headers = {
                            'Accept': 'application/json',
                            'Authorization': 'Bearer ' + message.content,
                        }

                        response = requests.get(url, headers=headers, cookies=cookies)

                        # If API token is verified to be correct, continues
                        if str(response) == "<Response [200]>":

                            # Formats response for servers in JSON format
                            servers_json_response = response.json()

                            user_client = False
                            user_subuser = False
                            user_crabwings = False
                            user_duckfeet = False
                            for server in servers_json_response['data']:
                                server_owner = server['attributes']['server_owner']
                                if server_owner == True:
                                    user_client = True
                                elif server_owner == False:
                                    user_subuser = True
                                server_node = server['attributes']['node']
                                if server_node == "Crabwings - NYC":
                                    user_crabwings = True
                                elif server_node == "Duckfeet - EU":
                                    user_duckfeet = True
                            if user_client == True:
                                role = discord.utils.get(guild.roles, id=client_role_id)
                                await member.add_roles(role)
                            if user_subuser == True:
                                role = discord.utils.get(guild.roles, id=subuser_role_id)
                                await member.add_roles(role)
                            if user_crabwings == True:
                                role = discord.utils.get(guild.roles, id=crabwings_role_id)
                                await member.add_roles(role)
                            if user_duckfeet == True:
                                role = discord.utils.get(guild.roles, id=duckfeet_role_id)
                                await member.add_roles(role)
                            role = discord.utils.get(guild.roles, id=verified_role_id)
                            await member.add_roles(role)
                    
                    await channel.send ('Your Discord account has been linked to your panel account! You may unlink your Discord and panel accounts by reacting in the #verification channel or by deleting your Verification API key.')
                    print("Success message sent to " + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")" + ". User linked to API key " + message.content + " and client_id " + str(json_response['attributes']['id']))     
                elif client_id_already_exists:
                    await channel.send('Sorry, your panel account is already linked to a Discord account. If you would like to link your panel account to a different Discord account, please unlink your panel account first by deleting its Verification API key and waiting up to 10 minutes.')
                    print("Duplicate panel message sent to " + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")" + " for using API key " + message.content + " linked to client_id " + str(json_response['attributes']['id']))
                elif discord_id_already_exists:
                    await channel.send('Sorry, your Discord account is already linked to a panel account. If you would like to link your Discord account to a different panel account, please unlink your Discord account first by reacting in the #verification channel.')
                    print("Duplicate Discord message sent to " + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")" + " for using API key " + message.content + " linked to client_id " + str(json_response['attributes']['id']))

            # Makes json pretty with indentations and stuff, then writes to file
#                json_dumps = json.dumps(json_response, indent = 2)
#                file = open("data.json", "w")
#                file.write(json_dumps)
#                file.close()

#               linked_servers = {}
#               linked_servers['server'] = []
#               for server in json_response['data']:
#                   server_owner = server['attributes']['server_owner']
#                   server_uuid = server['attributes']['uuid']
#                   server_name = server['attributes']['name']
#                   server_node = server['attributes']['node']
#                   message_sender = message.author.id
#                   info = str(server_owner) + server_uuid + server_name + server_node + str(message_sender)
#                   print(info)
#                   file = open('/home/container/data/' + str(message.author.id) + '.json', "a")
#                   file.write(info + '\n')
#                   file.close()
            else: 
                #Says if API key is the corect # of characters but invalid
                await channel.send("Sorry, that appears to be an invalid API key.")
                print('invalid sent to ' + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")")
        else:
            #Says this if API key is incorrect # of characters
            await channel.send('Sorry, that doesn\'t appear to be an API token. An API token should be a long string resembling this: ```yQSB12ik6YRcmE4d8tIEj5gkQqDs6jQuZwVOo4ZjSGl28d46```')
            print("obvious incorrect sent to " + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")")
    
    elif len(message.attachments) > 0:
        if message.attachments[0].url.endswith(('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image')) == False:
            download = message.attachments[0].url
            r = requests.get(download, allow_redirects=True)
            text = r.text
            text = "\n".join(text.splitlines())
            if '�' not in text:  # If it's not an image/gif
                truncated = False
                if len(text) > 100000:
                    text = text[:99999]
                    truncated = True
                req = requests.post('https://bin.birdflop.com/documents', data=text)
                key = json.loads(req.content)['key']
                response = ""
                response = response + "https://bin.birdflop.com/" + key
                response = response + "\nRequested by " + message.author.mention
                if truncated:
                    response = response + "\n(file was truncated because it was too long.)"
                embed_var = discord.Embed(title="Please use a paste service", color=0x1D83D4)
                embed_var.description = response
                await message.channel.send(embed=embed_var)
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
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
        await member.send("Hey there! It looks like you'd like to verify your account. I'm here to help you with that!\n\nIf you're confused at any point, see https://birdflop.com/verification for a tutorial including images.\n\nWith that said, let's get started! You'll want to start by grabbing some API credentials for your account by signing into https://panel.birdflop.com. Head over to the **Account** section in the top right, then click on the **API Credentials tab**. You'll want to create an API key with description `Verification` and `172.18.0.2` in the **Allowed IPs section**.\n\nWhen you finish entering the necessary information, hit the blue **Create **button.\n\nNext, you'll want to copy your API credentials. After clicking **Create**, you'll receive a long string. Copy it with `ctrl+c` (`cmnd+c` on Mac) or by right-clicking it and selecting **Copy**.\n\nIf you click on the **Close **button before copying the API key, no worries! Delete your API key and create a new one with the same information.\n\nFinally, direct message your API key to Botflop: that's me!\n\nTo verify that you are messaging the key to the correct user, please ensure that the my ID is `Botflop#2403` and that my username is marked with a blue **BOT** badge. Additionally, the only server under the **Mutual Servers** tab should be Birdflop Hosting.\n\nAfter messaging me your API key, you should receive a success message. If you do not receive a success message, please create a ticket in the Birdflop Discord's #support channel.")
        print("sent verification challenge to " + member.name + "#" + str(member.discriminator) + " (" + str(member.id) + ")")
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
            json_dumps = json.dumps(data, indent = 2)
            file = open('users.json', 'w')
            file.write(json_dumps)
            file.close()
            await member.edit(roles=[])
            await member.send("Your Discord account has successfully been unlinked from your Panel account!")
            print('successfully unlinked ' + member.name + "#" + str(member.discriminator) + " (" + str(member.id) + ")")

@bot.command()
async def ping(ctx):
	await ctx.send(f'Your ping is {round(bot.latency * 1000)}ms')

@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    channel = await bot.fetch_channel(int(url.split("/")[5]))
    message = await channel.fetch_message(int(url.split("/")[6]))
    await message.add_reaction(reaction)
    print('reacted to ' + url + ' with ' + reaction)

@tasks.loop(minutes=10)
async def update_servers():
    print("synchronizing roles")
    file = open('users.json', 'r')
    data = json.load(file)
    file.close()
    guild = bot.get_guild(guild_id)
    i=-1
    for client in data['users']:
        i+=1
        member = guild.get_member(client['discord_id'])
        if member:
            api_key = client['client_api_key']
            url = "https://panel.birdflop.com/api/client"
            cookies = {
                'pterodactyl_session': 'eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%3D%3D',
            }
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + api_key,
            }
            response = requests.get(url, headers=headers, cookies=cookies)

            # If API token is verified to be correct, continues
            if str(response) == "<Response [200]>":
                # Formats response for servers in JSON format
                servers_json_response = response.json()

                user_client = False
                user_subuser = False
                user_crabwings = False
                user_duckfeet = False
                for server in servers_json_response['data']:
                    server_owner = server['attributes']['server_owner']
                    if server_owner == True:
                        user_client = True
                    elif server_owner == False:
                        user_subuser = True
                    server_node = server['attributes']['node']
                    if server_node == "Crabwings - NYC":
                        user_crabwings = True
                    elif server_node == "Duckfeet - EU":
                        user_duckfeet = True
                role = discord.utils.get(guild.roles, id=client_role_id)
                if user_client == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, id=subuser_role_id)
                if user_subuser == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, id=crabwings_role_id)
                if user_crabwings == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
                role = discord.utils.get(guild.roles, id=duckfeet_role_id)
                if user_duckfeet == True:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)
            else:
                data['users'].pop(i)
                json_dumps = json.dumps(data, indent = 2)
                file = open('users.json', 'w')
                file.write(json_dumps)
                file.close()                
                await member.edit(roles=[])
                print("removed discord_id " + str(client['discord_id']) + " with client_id " + str(client['client_id']) + " and INVALID client_api_key " + client['client_api_key'])
        else:
 #           file = open('oldusers.json', 'r')
 #           olddata = json.load(file)
 #           file.close()
            # Checks if user exists. If so, skips adding them to users.json
#            already_exists = False
#            for olduser in olddata['users']:
#                if olduser['discord_id'] == json_response['attributes']['id']:
#                    
#            if already_exists == False:
#                olddata['users'].append({
#                    'discord_id': message.author.id,
#                    'client_id': json_response['attributes']['id'],
#                    'client_api_key': message.content
#                })
#                json_dumps = json.dumps(olddata, indent = 2)
#                file = open('oldusers.json', 'w')
#                file.write(json_dumps)
#                file.close()
            data['users'].pop(i)
            json_dumps = json.dumps(data, indent = 2)
            file = open('users.json', 'w')
            file.write(json_dumps)
            file.close()
            print("removed discord_id " + str(client['discord_id']) + " with client_id " + str(client['client_id']) + " and client_api_key " + client['client_api_key'])

@update_servers.before_loop
async def before_update_servers():
    print('waiting to enter loop')
    await bot.wait_until_ready()

update_servers.start()
bot.run(token)

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
