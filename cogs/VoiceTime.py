from VoiceModule import *
from Voiceclass import *
from discord.ext import commands
from discord_components import *
from datetime import datetime

class VoiceTime(commands.Cog):
    def __init__(self, client):
        self.client = client    
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Module >>> VoiceTime')
        DiscordComponents(self.client)

    @commands.Cog.listener()            
    async def on_voice_state_update(self, member, last, now):
        # sourcery no-metrics
        guild = member.guild
        if member.bot: return
        
        c : load_guild = load_guild(guild)
        if not c.okay: return
        l = lambda text: language(text, c.lang)

        ###############################
        ####### TODO Disconnect #######
        ###############################
        while last.channel in c.channels: 
            if last.channel == now.channel: return
            vt : VoiceClass= c.get_channel(last.channel)            
        
            if not last.channel.members: break
            if member not in vt.members: return
            is_owner = '**(owner)**' if member == vt.owner else ''
            try:
                last_message = await vt.chat.fetch_message(vt.chat.last_message_id)
                date_time = datetime.now().strftime('%m.%d - %H:%M')
                if vt.date == date_time:
                    date = ''
                else:           
                    date = f'\n**{date_time}**'
                    vt.date = date_time

                if vt.privat:
                    vt.set_cooldown(member)
                else:    
                    vt.rem(member)
                    await vt.chat.set_permissions(member, view_channel = False)
            
                mess = vt.message_content + l('{}\n> {} {} hat verlassen!').format(date, member.mention, is_owner)
                vt.message_content = mess
                if last_message == vt.message:
                    await last_message.edit(embed = embed('VoiceChat', mess))
                else:
                    await vt.message.delete()
                    message = await vt.chat.send(embed = embed('VoiceChat', mess))
                    vt.message = message
                break
            except: pass
            
        ###############################
        ######### TODO Normal #########
        ###############################
        if now.channel in [c.normal, c.privat]:
            channel = now.channel
            name, privat = ('||', False) if channel == c.normal else ('Privat', True)
            finish = False
            await c.normal.set_permissions(member, connect = False)
            await c.privat.set_permissions(member, connect = False)

            vc = await guild.create_voice_channel(
                name=f'{name} {member.display_name}', 
                category=c.privat.category if privat else c.normal.category)

            async def checker(member_id):  # sourcery skip: remove-redundant-if
                while not finish:
                    member, *_ = await self.client.wait_for('voice_state_update', check = lambda member, _, now: now.channel == vc and member.id != member_id)
                    if finish: break

                    if member.voice: await member.move_to(None)
                    await member.send(embed = voice(l('Du kannst den Channel nicht beitreten da der Channel gerade erstellt wird bitte versuche es gleich nochmal!'), 'red'))
                    #TODO add disable button 


            self.client.loop.create_task(checker(member.id))

            if member.voice:
                await member.move_to(vc)

            chat = await guild.create_text_channel(
                name=f'Voice Chat',
                category=c.setting.category)
                

            pin1 = await chat.send(embed = embed(l('Voice Chat von {}').format(member.name), l('Das ist der Voice Chat von {} hier kannst du mit den Leuten aus dem Voice Chat Nachrichten verschicken').format(member.mention)))
            pin2 = await chat.send(embed = embed(l('INFO'), l('Du kannst diesen Text Channel nur solange sehen wie du auch im jeweiligen Sprachkanal bist!'), 'o'))

            message_content = l('**{} hat den Channel um {} am {} erstellt!**\n').format(member.mention, datetime.now().strftime('%H:%M'), datetime.now().strftime('%m.%d'))
            mess = await chat.send(embed = embed('VoiceChat', message_content))

            vt = VoiceClass(self.client, data, fl, member, vc, chat, privat, mess, message_content)
            finish = True

            await pin1.pin()
            await pin2.pin()

            await vc.set_permissions(member, connect = True, manage_channels=True)
            await chat.set_permissions(member, read_messages=True)
            await chat.set_permissions(guild.default_role, read_messages=False)
            await c.normal.set_permissions(member, connect = True)
            await c.privat.set_permissions(member, connect = True)


            if vc.members:
                await self.client.wait_for('voice_state_update', check = lambda *_: not vc.members)
            if guild.get_channel(vc.id):
                await vc.delete()
            if guild.get_channel(chat.id):
                await chat.delete()

            c.delete(vt)
            
            return
        
        ###############################
        ######### TODO Join ###########
        ###############################
        if now.channel not in c.channels:
            return
        
        if last.channel == now.channel: return
        
        # Variable
        channel = now.channel
        vt = c.get_channel(channel)

        # Whitelist
        async def whitelist():
            vt.add(member)
            try:
                await vt.chat.set_permissions(member, view_channel = True)
                await vt().set_permissions(member, connect = True)

                is_owner = '**(owner)**' if member == vt.owner else ''
                last_message = await vt.chat.fetch_message(vt.chat.last_message_id)
                date_time = datetime.now().strftime('%m.%d - %H:%M')
                if vt.date == date_time:
                    date = ''
                else:
                    date = f'\n**{date_time}**'
                    vt.date = date_time
                    
                mess = vt.message_content + l('{}\n> {} {} ist beigetreten!').format(date, member.mention, is_owner)
                vt.message_content = mess
                if last_message == vt.message:
                    await last_message.edit(embed = embed('VoiaceChat', str(mess)))
                else:
                    await vt.message.delete()
                    message = await vt.chat.send(embed = embed('VoiceChat', mess))
                    vt.message = message
            except:
                pass

        # Check if ENTER
        if member in vt.members or not vt.privat:
            await whitelist()
            return
        
        if member == vt.owner:
            await whitelist()
            return

        if member in vt.friends:
            await whitelist()
            return        
        
        # Start of Whitelisting

        # Queue
        if c.queue:
            await member.move_to(c.queue)
            if not member.voice.mute:
                async def queue(member, c):
                    await member.edit(mute = True)
                    await self.client.wait_for('voice_state_update', check = lambda m, l, _: member == m and l.channel == c.queue)
                    await member.edit(mute = False)

                self.client.loop.create_task(queue(member, c))
        else:
            await member.move_to(None)


        await channel.set_permissions(member, connect = False)

        
        async def check(event):
            if not event:
                if guild.get_channel(channel.id):
                    await channel.set_permissions(member, connect = True)
                return True
        
            if event.user == vt.owner:
                await event.message.delete()
                if event.component.id == '1':
                    return True

            if event.user == member and event.component.id == '2':
                await event.message.delete()
                return await event.respond(content = l('In dem du auf Nein gedrückt hast, hast du die Anfrage abgebrochen!'))
            
            await respond(event)
        
        mess = await send(c.setting, button(l('Ja'), ButtonStyle.green), button(l('Nein'), ButtonStyle.red, id=2) ,mess= str(vt.owner.mention), embed = (*v('Darf {} beitreten?'), member.mention), time = 30, check = check)

        await whitelist()          
        

        # Direct Message
        if c.queue:
            if member in c.queue.members:
                if guild.get_channel(channel.id):
                        await member.move_to(channel)  
        elif not c.privat_notification(member):
            link = await channel.create_invite(max_age = 300)
            mess = await member.send(embed = voice(l('Du kannst nun in Channel {} von {} beitreten!').format(vt().mention, vt.owner.mention)), 
                #components = [[Button(label= l('beitreten'), style=ButtonStyle.blue),  Button(label = l('Deaktiviere diese Benachrichtigung'), style=ButtonStyle.red)]]
                components = [[button(l('beitreten'), ButtonStyle.URL, url = f'{link}'),button(l('Deaktiviere diese Benachrichtigung'), ButtonStyle.red)]]
            )
            event = await wait_button(self.client, mess, 30)
            if not event:
                await mess.edit(component = [button(l('Deaktiviere diese Benachrichtigung'), ButtonStyle.red, disabled = True)])
                return
            await event.respond(type = 6)

            data['user_setting']['no_privat_notification'].append(member)


            await member.send(embed = voice(l('Private Benachrichtigung wurde deaktiviert!'), 'green'))
            await member.send(embed = info(l('Wenn du sie wieder aktivieren willst, gehe auf einem Server und gebe `//set notification on` ein.')))           
        
def setup(client):
    client.add_cog(VoiceTime(client))