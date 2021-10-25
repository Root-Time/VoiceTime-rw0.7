from discord.ext import commands
from VoiceModule import * 
from Voiceclass import * 

class setting(commands.Cog):
    def __init__(self, client):
        self.client =client 
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Module >>> Setting')

    @commands.command()
    async def entmute(self, ctx):
        await ctx.author.edit(mute = False)
        await ctx.author.edit(deafen = False)


    @commands.command()
    async def set(self, ctx, *args):
        if args[0] == 'lang':
            lang = args[1]
            with open('Data/LanguesForm.yml', 'r'):
                pass
            load_guild(ctx.guild).set_lang(lang)
            await ctx.channel.send(f'PLACEHOLDER: Langues set to {args[1]}')

    @commands.command()
    async def lol(self, ctx):
        print(data)

def setup(client):
    client.add_cog(setting(client))