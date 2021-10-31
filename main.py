import discord
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, MemberNotFound
from VoiceModule import *


PREFIX = '!!'
INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS)


@bot.event
async def on_ready():
    print(f'>>>>  {bot.user.name}  <<<<')
    print('>>>> ', datetime.now().strftime("%H:%M:%S"),' <<<<')
    print('--------------------')
    await start(bot)


bot.load_extension("cogs.VoiceTime")
bot.load_extension("cogs.newServer")
#bot.load_extension("cogs.Language_converter")
bot.load_extension("cogs.setting")
bot.load_extension("cogs.Utility")
bot.load_extension("cogs.VoiceCommands")

@bot.command()
async def main(ctx):
    await ctx.send('pong')

@bot.command()
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound): return
    if isinstance(error, MemberNotFound): 
        return await ctx.channel.send(embed=embed('Error', 'Du hast keinen gültigen Namen eingegeben', 10038562), delete_after=5)
    raise error
    


bot.run(TOKEN)
