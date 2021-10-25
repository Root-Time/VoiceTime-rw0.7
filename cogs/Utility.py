import discord, json, copy
from discord.ext import commands
from VoiceModule import *


class Utility(commands.Cog):
    def __init__(self, client):
        self.client =client 

    @commands.command()
    async def d(self, ctx):
        data2 = copy.deepcopy(data)
        data2[ctx.guild.id]['voice'] = []

        await ctx.send(f'```json\n{json.dumps(data2, indent=4)}```')



    @commands.command()
    async def delete(self, ctx):
        for i in ctx.guild.channels:
            if 'Time' in i.name or 'voice-chat' in i.name:
                try:
                    await i.delete()
                except: pass


    @commands.command()
    async def dd(self, ctx):
        await ctx.send(str(data))

def setup(client):
    client.add_cog(Utility(client))
