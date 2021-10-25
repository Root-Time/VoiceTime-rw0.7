from discord.ext import commands
from VoiceModule import * 
from Voiceclass import * 
import datetime

class VoiceCommands(commands.Cog):
    def __init__(self, client):
        self.client =client 
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Module >>> VoiceCommands')
        
    """         async def saving():
            await asyncio.sleep(5)
            with open('Data/Friendlist.yaml', 'w') as f:
                fl = fll()
                for i in fl.keys:
                    fl[i.id] = fl[i]
                
                print(fl)

                yaml.dump(fll(), f)
        self.client.loop.create_task(saving())  """
        

    
    @commands.command()
    async def afriend(self, ctx, *args):
        print(fl)
        await ctx.send(fl or 'RIPPP')

    @commands.command(aliases = ['rem'])
    async def remove(self, ctx, player: discord.Member = False):
        if player is ctx.author:
            await ctx.channel.send(embed=embed('Error', 'Du kannst dich nicht selbst von deiner Freundesliste enfernen!', 10038562), delete_after = 5)
            return

        if not player: 
            await ctx.channel.send(embed=embed('Error', 'Du hast kein User angegeben!', 10038562), delete_after = 5)
            return
        owner = ctx.author
        c = load_guild(ctx.guild)
        log_channel = c.logs
        if owner not in fl.keys():
            await ctx.channel.send(embed=embed('Friend System', f'<@{owner.id}> hat noch keine Freunde!', 10038562), delete_after = 5)
            return

        if player not in fl[owner]:
            await ctx.channel.send(embed=embed('Friend System', f'<@{owner.id}> und <@{player.id}> wart nie Freunde!', 10038562), delete_after = 5)
            return


        c.rem_friend(owner, player)
        """   self.d_friends[owner.id].remove(player.id)
        self.d_friends[player.id].remove(ctx.author.id)
        if not self.d_friends[owner.id]: 
            del self.d_friends[owner.id] 
        if not self.d_friends[player.id]:
            del self.d_friends[player.id]  """

        await ctx.channel.send(embed=embed('Friend System', f'<@{player.id}> und <@{owner.id}> sind keine Freunde mehr!', 9936031), delete_after = 5)
        await log_channel.send(embed=embed('Friend System', f'<@{owner.id}> hat <@{player.id}> von seiner Freundesliste enfernt\n{datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}'))
        """ with open('friends.yml', 'w')  as f:
            yaml.dump(self.d_friends, f)  """

    @commands.command(aliases=['friend'])
    async def add(self, ctx, player: discord.Member = False):
        await ctx.message.delete()
        owner = ctx.author
        guild = ctx.guild

        if not player: 
            await ctx.channel.send(embed=embed('Error', 'Du hast kein Member eingetragen!', 10038562), delete_after = 5)
            return

        if owner == player:
            return await ctx.channel.send(embed=embed('Error','Du kannst dir selber keine Freundschaftsanfrage schicken!', 10038562), delete_after = 5)

        c = load_guild(guild)
        l = lambda text: language(text, c.lang)

        if player in c.friends(owner):
            await ctx.channel.send(embed=embed('Friend System', f'<@{owner.id}> und <@{player.id}> sind schon befreundet!', 10038562), delete_after=5)
            return

            
        temp = await ctx.channel.send(f'{player.mention}')
        await temp.delete()
        #await send(f'{owner.mention}',ctx.channel, embed('Friend System', f'<@{player.id}>\n<@{ctx.author.id}> hat dir eine Freundschaftsanfrage geschickt!',15105570), button(l('Ja'), ButtonStyle.green), button(l('Nein'), ButtonStyle.red, id=2), 30)
        
        #mess = await ctx.channel.send(embed=embed('Friend System', f'<@{player.id}>\n<@{ctx.author.id}> hat dir eine Freundschaftsanfrage geschickt!',15105570), delete_after = 120)

        mess = await send(ctx.channel, button(l('Ja'), ButtonStyle.blue), button(l('Nein'), ButtonStyle.gray, 2), embed = ('Friend System', f'<@{player.id}>\n<@{ctx.author.id}> hat dir eine Freundschaftsanfrage geschickt!', 'b'))

        while True:
            event = await wait_button(self.client, mess)
            if event.author != player:
                await respond(event)
                continue
            break
        
        await event.respond(type = 6)

        c.add_friend(owner, player)

        await mess.delete()
        await ctx.channel.send(embed = embed('Friend System', l('Ihr seit nun Freunde!'), 'b'), delete_after = 10)
    
    @commands.command()
    async def load(self, ctx, player: discord.Member = False):
        if not player: player = ctx.author
        owner_fl = fl.get(player)
        if not owner_fl:
            embed1 = embed('Friend List', f'<@{player.id}> hat noch keine Freunde!', 10038562)
            embed1.set_author(name= player.display_name, icon_url = player.avatar_url)
            await ctx.channel.send(embed=embed1, delete_after= 10)
            return

        c = load_guild(ctx.guild)
        l = lambda text: language(text, c.lang)

        text = '\n'.join(f'{friend.mention}' for friend in owner_fl)

        friends_list_embed = discord.Embed(title='Friend List', description=text, colour=15105570)
        friends_list_embed.set_author(name= player.display_name, icon_url = player.avatar_url)
        async def check(event):
            if event.author in [ctx.author, player]:
                await event.message.delete()
                return True
            await respond(event)

        mess = await send(ctx.channel, button(l('Schließen'), ButtonStyle.red), embed = friends_list_embed, time = 15, check = check)

def setup(client):
    client.add_cog(VoiceCommands(client))