import os
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

class Linking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild_id = int(os.getenv('guild_id'))
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.bot.user and message.guild == None:
            channel = message.channel
            await channel.send("Processing, please wait...")
            # Potential API key, so tries it out
            if len(message.content) == 48:
                url = "https://panel.birdflop.com/api/client/account"

                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + message.content,
                }

                # response = requests.get(url, headers=headers)

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:

                        # If API token is verified to be correct:
                        if response.status == 200:

                            # Formats response of account in JSON format
                            json_response = await response.json()

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
                                    logging.info("Client ID already exists")
                                if user['discord_id'] == message.author.id:
                                    discord_id_already_exists = True
                                    logging.info("Discord ID already exists")
                            if client_id_already_exists == False and discord_id_already_exists == False:
                                data['users'].append({
                                    'discord_id': message.author.id,
                                    'client_id': json_response['attributes']['id'],
                                    'client_api_key': message.content
                                })
                                json_dumps = json.dumps(data, indent=2)
                                # Adds user to users.json
                                file = open('users.json', 'w')
                                file.write(json_dumps)
                                file.close()

                                guild = self.bot.get_guild(self.guild_id)
                                member = guild.get_member(message.author.id)
                                if member:

                                    url = "https://panel.birdflop.com/api/client"

                                    headers = {
                                        'Accept': 'application/json',
                                        'Authorization': 'Bearer ' + message.content,
                                    }

                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(url, headers=headers) as response:

                                            # If API token is verified to be correct, continues
                                            if response.status == 200:

                                                # Formats response for servers in JSON format
                                                servers_json_response = await response.json()

                                                user_client = False
                                                user_subuser = False
                                                user_crabwings = False
                                                user_duckfeet = False
                                                user_elktail = False
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
                                                    elif server_node == "Elktail - EU":
                                                        user_elktail = True
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
                                                if user_elktail == True:
                                                    role = discord.utils.get(guild.roles, id=elktail_role_id)
                                                    await member.add_roles(role)
                                                role = discord.utils.get(guild.roles, id=verified_role_id)
                                                await member.add_roles(role)

                                await channel.send(
                                    'Your Discord account has been linked to your panel account! You may unlink your Discord and panel accounts by reacting in the #verification channel or by deleting your Verification API key.')
                                logging.info("Success message sent to " + message.author.name + "#" + str(
                                    message.author.discriminator) + " (" + str(
                                    message.author.id) + ")" + ". User linked to API key " + message.content + " and client_id " + str(
                                    json_response['attributes']['id']))
                            elif discord_id_already_exists:
                                await channel.send(
                                    'Sorry, your Discord account is already linked to a panel account. If you would like to link your Discord account to a different panel account, please unlink your Discord account first by reacting in the #verification channel.')
                                logging.info("Duplicate Discord message sent to " + message.author.name + "#" + str(
                                    message.author.discriminator) + " (" + str(
                                    message.author.id) + ")" + " for using API key " + message.content + " linked to client_id " + str(
                                    json_response['attributes']['id']))
                            elif client_id_already_exists:
                                await channel.send(
                                    'Sorry, your panel account is already linked to a Discord account. If you would like to link your panel account to a different Discord account, please unlink your panel account first by deleting its Verification API key and waiting up to 10 minutes.')
                                logging.info("Duplicate panel message sent to " + message.author.name + "#" + str(
                                    message.author.discriminator) + " (" + str(
                                    message.author.id) + ")" + " for using API key " + message.content + " linked to client_id " + str(
                                    json_response['attributes']['id']))
                        else:
                            # Says if API key is the corect # of characters but invalid
                            await channel.send("Sorry, that appears to be an invalid API key.")
                            logging.info(
                                'invalid sent to ' + message.author.name + "#" + str(message.author.discriminator) + " (" + str(
                                    message.author.id) + ")")
            else:
                # Says this if API key is incorrect # of characters
                await channel.send(
                    'Sorry, that doesn\'t appear to be an API token. An API token should be a long string resembling this: ```yQSB12ik6YRcmE4d8tIEj5gkQqDs6jQuZwVOo4ZjSGl28d46```')
                logging.info("obvious incorrect sent to " + message.author.name + "#" + str(
                    message.author.discriminator) + " (" + str(message.author.id) + ")")

def setup(bot):
    bot.add_cog(Linking(bot))
