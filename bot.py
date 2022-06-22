import os
import discord
import json
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import aiohttp
import mimetypes
import requests
# import subprocess

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents,
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
        if message.author.bot:
            return
        perms = message.channel.permissions_for(message.guild.me)
        if not perms.send_messages:
            return
        if not message.attachments[0].url.lower().endswith(('.html')):
            file_type = mimetypes.guess_type(message.attachments[0].url)
            if not file_type[0] == None:
                try:
                    file_type = file_type[0].split('/')[0]
                except:
                    logging.info(file_type + " failed while being parsed")
            if message.attachments[0].url.lower().endswith(('.log', '.txt', '.json', '.yml', '.yaml', '.css', '.py', '.js', '.sh', '.config', '.conf')) or file_type == 'text':
                text = await discord.Attachment.read(message.attachments[0], use_cached=False)
                text = text.decode('Latin-1')
                text = "\n".join(text.splitlines())
                truncated = False
                if len(text) > 100000:
                    text = text[:99999]
                    truncated = True
                async with aiohttp.ClientSession() as session:
                    async with session.post('https://bin.birdflop.com/documents', data=text) as req:
                        key = json.loads(await req.read())['key']
                response = ""
                response = response + "https://bin.birdflop.com/" + key
                response = response + "\nRequested by " + message.author.mention
                if truncated:
                    response = response + "\n(file was truncated because it was too long.)"
                embed_var = discord.Embed(title="Please use a paste service", color=0x1D83D4)
                embed_var.description = response
                try:
                    await message.channel.send(embed=embed_var)
                except:
                    print("Permission error")
                logging.info(f'File uploaded by {message.author} ({message.author.id}): https://bin.birdflop.com/{key}')
    # Pastebin is blocked in some countries
    words = message.content.replace("\n", " ").split(" ")
    for word in words:
        if word.startswith("https://pastebin.com/") and len(word) == 29:
            print("hello3")
            pastebinkey = word[len(word) - 8:]
            r = requests.get(f'https://pastebin.com/raw/{pastebinkey}')
            text = r.text
            truncated = False
            if len(text) > 100000:
                text = text[:99999]
                truncated = True
            async with aiohttp.ClientSession() as session:
                async with session.post('https://bin.birdflop.com/documents', data=text) as req:
                    key = json.loads(await req.read())['key']
            response = ""
            response = response + "https://bin.birdflop.com/" + key
            response = response + "\nRequested by " + message.author.mention
            if truncated:
                response = response + "\n(file was truncated because it was too long.)"
            embed_var = discord.Embed(title="Pastebin is blocked in some countries", color=0x1D83D4)
            embed_var.description = response
            try:
                await message.channel.send(embed=embed_var)
            except:
                print("Permission error")
    timings = bot.get_cog('Timings')
    await timings.analyze_timings(message)
    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction):
    if interaction.type.name == 'component':
        if str(interaction.user.id) in interaction.data['custom_id']:
          timings = bot.get_cog('Timings')
          if 'prev' in interaction.data['custom_id']:
              await timings.analyze_timings(interaction.message, interaction)
          if 'next' in interaction.data['custom_id']:
              await timings.analyze_timings(interaction.message, interaction)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Birdflop bot ping is {round(bot.latency * 1000)}ms')
@bot.command()
async def privacy(ctx):
    await ctx.send('You can view the bot\'s privacy policy at https://bin.birdflop.com/ohopawewok.txt.')
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
