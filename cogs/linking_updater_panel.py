import os
import discord
import requests
import json
import logging
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import aiohttp
import asyncio

class Linking_updater(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild_id = int(os.getenv('guild_id'))
        self.crabwings_role_id = int(os.getenv('crabwings_role_id'))
        self.duckfeet_role_id = int(os.getenv('duckfeet_role_id'))
        self.elktail_role_id = int(os.getenv('elktail_role_id'))
        self.client_role_id = int(os.getenv('client_role_id'))
        self.subuser_role_id = int(os.getenv('subuser_role_id'))
        self.verified_role_id = int(os.getenv('verified_role_id'))

    @tasks.loop(minutes=10)
    async def linking_updater(self):
        logging.info("Synchronizing roles")
        file = open('users.json', 'r')
        data = json.load(file)
        file.close()
        guild = self.bot.get_guild(self.guild_id)
        i = -1
        for client in data['users']:
            i += 1
            member = guild.get_member(client['discord_id'])
            if member:
                api_key = client['client_api_key']
                url = "https://panel.birdflop.com/api/client"
                headers = {
                    'Accept': 'application/json',
                    'Authorization': 'Bearer ' + api_key,
                }
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
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
                            role = discord.utils.get(guild.roles, id=self.client_role_id)
                            if user_client == True:
                                await member.add_roles(role)
                            else:
                                await member.remove_roles(role)
                            role = discord.utils.get(guild.roles, id=self.subuser_role_id)
                            if user_subuser == True:
                                await member.add_roles(role)
                            else:
                                await member.remove_roles(role)
                            role = discord.utils.get(guild.roles, id=self.crabwings_role_id)
                            if user_crabwings == True:
                                await member.add_roles(role)
                            else:
                                await member.remove_roles(role)
                            role = discord.utils.get(guild.roles, id=self.duckfeet_role_id)
                            if user_duckfeet == True:
                                await member.add_roles(role)
                            else:
                                await member.remove_roles(role)
                            role = discord.utils.get(guild.roles, id=self.elktail_role_id)
                            if user_elktail == True:
                                await member.add_roles(role)
                            else:
                                await member.remove_roles(role)
                        else:
                            data['users'].pop(i)
                            json_dumps = json.dumps(data, indent=2)
                            file = open('users.json', 'w')
                            file.write(json_dumps)
                            file.close()
                            await member.edit(roles=[])
                            logging.info("removed discord_id " + str(client['discord_id']) + " with client_id " + str(
                                client['client_id']) + " and INVALID client_api_key " + client['client_api_key'])
            else:
                data['users'].pop(i)
                json_dumps = json.dumps(data, indent=2)
                file = open('users.json', 'w')
                file.write(json_dumps)
                file.close()
                logging.info("removed discord_id " + str(client['discord_id']) + " with client_id " + str(
                    client['client_id']) + " and client_api_key " + client['client_api_key'])

    @linking_updater.before_loop
    async def before_linking_updater(self):
        logging.info('waiting to enter loop')
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(Linking_updater(bot))
