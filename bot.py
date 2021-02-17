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

# import subprocess

bot = commands.Bot(command_prefix=".", intents=discord.Intents.default(),
                   case_insensitive=True)

load_dotenv()
token = os.getenv('token')

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
    # Binflop
    if len(message.attachments) > 0:
        if not message.attachments[0].url.endswith(
                ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image', '.svg', '.jar', ',zip', '.tar', '.gz', '.msi', '.exe', '.html')):
            text = await discord.Attachment.read(message.attachments[0], use_cached=False)
            text = text.decode('Latin-1')
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
                logging.info(f'File uploaded by {message.author} ({message.author.id}): https://bin.birdflop.com/{key}')
    timings = bot.get_cog('Timings')
    await timings.analyze_timings(message)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Birdflop bot ping is {round(bot.latency * 1000)}ms')

@bot.command()
async def invite(ctx):
    await ctx.send('Invite me with this link:\nhttps://discord.com/oauth2/authorize?client_id=787929894616825867&permissions=0&scope=bot')

@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    channel = await bot.fetch_channel(int(url.split("/")[5]))
    message = await channel.fetch_message(int(url.split("/")[6]))
    await message.add_reaction(reaction)
    logging.info('reacted to ' + url + ' with ' + reaction)

for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')


bot.run(token)

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
