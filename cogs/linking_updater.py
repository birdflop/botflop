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

class Linking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild_id = int(os.getenv('guild_id'))
        self.crabwings_role_id = int(os.getenv('crabwings_role_id'))
        self.duckfeet_role_id = int(os.getenv('duckfeet_role_id'))
        self.elktail_role_id = int(os.getenv('elktail_role_id'))
        self.client_role_id = int(os.getenv('client_role_id'))
        self.subuser_role_id = int(os.getenv('subuser_role_id'))
        self.verified_role_id = int(os.getenv('verified_role_id'))
