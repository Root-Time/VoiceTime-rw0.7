import asyncio, json
from datetime import datetime, time

class load_guild_with_data:
    def __init__(self, guild, data, fl ,ss ,us):
        self.full_data = data
        self.data = data.get(guild.id) or print('Error')
        self.fl = fl 
        if not self.data:
            self.okay = False
            return  
        self.guild = guild
        self.okay = True

        self.timeout = self.full_data['timeout']
        self.normal = self.guild.get_channel(self.data['Normal_Channel'])
        self.privat = self.guild.get_channel(self.data['Privat_Channel'])
        self.logs = self.guild.get_channel(self.data['Voice_Logs_Chat'])
        self.setting = self.guild.get_channel(self.data['Voice_Setting_Chat'])
        self.config = self.guild.get_channel(self.data['Config'])
        self.queue = self.guild.get_channel(self.data["Queue"])
        
        self.lang = self.data["Langues"]
        self.is_logs_public = self.data['Voice_Logs_Public']
        
        self.voice = self.data['voice']
        self.friendss = self.data['friends']
        self.channels = [i() for i in self.voice]
        #Voice
    
    def privat_notification(self, member):
        return member in self.full_data['user_setting']['no_privat_notification']
        

    def get_channel(self, attr):
        for i in self.voice:
            if attr == i():
                return i


    def friends(self, friend):
        return self.fl.get(friend, []) 
        

    def add_friend(self, friend, friend2):
        self.fl.setdefault(friend, []).append(friend2)
        self.fl.setdefault(friend2, []).append(friend)
        self.full_data["friends"].setdefault(friend, []).append(friend2)
        
        


    def rem_friend(self, friend, friends2):
        self.full_data["friends"].get(friend, [friends2]).remove(friends2)
        self.fl.get(friend, [friends2]).remove(friends2)
        self.fl.get(friends2, [friend]).remove(friend)

    def channels_by(self, member):
        return [i for i in self.voice if i.owner == member]

    
    def delete(self, channel):
        if channel not in self.voice:
            return
        
        self.voice.remove(channel)

async def delete(self, member):
    await asyncio.sleep(360)
    await self.rem(member)
    await self.chat.set_permissions(member, view_channel = False)  

class VoiceClass():
    def __init__(self, client, data, fl, owner, vc, chat, privat, message, message_content):
        self.guild = owner.guild
        self.owner = owner
        self.id = vc.id
        self.chat = chat
        self.privat = privat
        self.members = set([owner])
        self._vc = vc
        self.client = client
        self.message_content = message_content
        self.message = message
        self.member_cooldown = {}
        self.data = data
        self.date = None
        data[self.guild.id]['voice'].append(self)
        self.friends = fl.get(owner)

    def add(self, member):
        self.members.add(member) 

    def rem(self, member):
        self.members.remove(member)

    

    def cooldown(self, member = None, show = False):
        if member:
            cooldown = self.member_cooldown.get(member)
            if show:
                return cooldown
            return cooldown <= datetime.now()
        return self.member_cooldown.keys()
        

    def set_cooldown(self, member):
        self.member_cooldown[member] = datetime.now()
        
        self.client.loop.create_task(delete(self, member))



    def set(self, owner):
        self.owner = owner
    
    def toggle_privat(self, privat):
        self.privat = privat
    
    def __copy__(self):
        return None
    def __deepcopy__(self, _):
        return None

    def __call__(self):
        return self._vc



    