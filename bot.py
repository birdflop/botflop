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
import paramiko

# import subprocess

bot = commands.Bot(command_prefix=".", intents=discord.Intents.default(),
                   case_insensitive=True)
load_dotenv()

token = os.getenv('token')
crabwings_role_id = int(os.getenv('crabwings_role_id'))
duckfeet_role_id = int(os.getenv('duckfeet_role_id'))
elktail_role_id = int(os.getenv('elktail_role_id'))
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

@bot.event
async def on_message(message):
    if not running_on_panel:
        # Binflop
        if len(message.attachments) > 0:
            if not message.attachments[0].url.endswith(
                    ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image')):
                download = message.attachments[0].url
                async with aiohttp.ClientSession() as session:
                    async with session.get(download, allow_redirects=True) as r:

                        # r = requests.get(download, allow_redirects=True)
                        text = await r.text()
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
        timings = bot.get_cog('Timings')
        await timings.analyze_timings(message)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    if running_on_panel:
        if guild_id == ctx.guild.id:
            await ctx.send(f'Private bot ping is {round(bot.latency * 1000)}ms')
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
