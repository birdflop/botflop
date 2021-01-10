import discord
from discord.ext import commands, tasks



class Linking_updater(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=10)
    async def linking_updater(self):
        print("Hello2")
        
    @linking_updater.before_loop
    async def before_linking_updater(self):
        print("Hello")
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(Linking_updater(bot))

linking_updater.start()
