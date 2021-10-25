import discord
import logging
import asyncio
import json, yaml
from discord_components import *
from Voiceclass import *
import logging
from threading import Thread

log = logging

log.basicConfig(filename='Logs/ERROR.log', format = '%(asctime)s %(levelname)s: %(message)s', datefmt= '%d/%m %I:%M:%S',filemode = 'w', encoding='utf-8', level=logging.ERROR)
client = None
check = True

from time import sleep

async def start(_client):
    global client
    client = _client
    while True:
        if not client:
            continue
        for i in temp_fl.keys():
            
            fl[await client.fetch_user(i)] = [await client.fetch_user(ii) for ii in temp_fl[i]]
        break

def json_int(dictionary):
    alist = []
    for key in dictionary.keys():
        try:
            int(key)
            alist.append(key)     
        except: pass
        if isinstance(dictionary[key], dict):
            json_int(dictionary[key])
    for key in alist:
        dictionary[int(key)] = dictionary[key]
        del dictionary[key]

with open('Data/config.json', 'r') as f:
    log.info('Data/config.json has loadet')
    data = json.load(f)
    json_int(data)
with open('Data/Server_Setting.yaml') as Server_Setting:
    ss = yaml.load(Server_Setting, Loader = yaml.FullLoader) or {}
with open('Data/User_Setting.yaml') as User_Setting:
    us = yaml.load(User_Setting, Loader = yaml.FullLoader) or {}
with open('Data/Friendlist.yaml') as Friendlist:
    temp_fl = yaml.load(Friendlist, Loader = yaml.FullLoader) or {}
    fl = {}



def load_guild(guild):
    return load_guild_with_data(guild, data, fl, ss, us)


# Embed 
def embed(title, description, c=0):
    if c in ['blue', 'b']: 
        c = 3447003  # blue
    elif c in ['red', 'r']: 
        c = 15158332 # red
    elif c in ['green', 'g']: 
        c = 3066993  # green
    elif c in ['orange', 'o']: 
        c = 15105570 # orange
    return discord.Embed(title=title, description=description, colour=c)

def error(text):
    return embed('Error', text, 'r')

def voice(text, color = "blue"):
    return embed('VoiceTime', text, color)

def info(text):
    return embed('Info', text, 'o')

def e(text):
    return ('Error', text, 'r')

def v(text, color = "blue"):
    return ('VoiceTime', text, color)

def i(text):
    return ('Info', text, 'o')

def language(text, l = "de"):
    with open("Data/language.json", 'r') as f:
        Voice_File = json.load(f)
    if not Voice_File:
        Voice_File = {}
    if text not in Voice_File.keys():
        Voice_File[text] = {'de': text}
        
    with open("Data/language.json", 'w') as f:
        json.dump(Voice_File, f, indent=4)

    if not Voice_File[text].get(l, None):
        return Voice_File[text]['de'] #Change to en
        
    return Voice_File[text][l]


"""async def send(*args):
    args = list(args)
    Message = None
    if isinstance(args[0], str):
        Message = args[0]
        args.remove(Message)
    channel = args[0]
    args.remove(channel)
    mess = args[0]
    args.remove(mess)
    time = None
    if isinstance(args[-1], int):
        time = args[-1]
        args.remove(time)
    if Message:
        return await channel.send(Message, embed=mess, components = [[i for i in args]], delete_after = time)
    return await channel.send(embed=mess, components = [[i for i in args]], delete_after = time)"""

async def send(channel, *args, **kwargs):
    """
    channel -> Discord Channel, 
    Button -> ButtonTyp
    Message -> str, 
    embed (Title, Text, Color or (Format), (Format)) -> tuple, 
    time (Delete After) -> Int, float, 
    check(for wait) -> function, 
    """
    embed = kwargs.get('embed')
    time = kwargs.get('time')
    check = kwargs.get('check')
    Message = kwargs.get('mess') or kwargs.get('Message')
    #load
    lang = 'de'

    
    if isinstance(embed, tuple):
        text = language(embed[1], lang)
        if len(embed) == 3:
            if isinstance(embed[2], tuple):
                _format = embed[2]
            else:
                colour = embed[2]
                _format = None
        elif len(embed) == 4:
            colour = embed[2]
            _format = embed[3]
        else:
            _format = None
            colour = None


        if _format:
            if isinstance(_format, str): 
                text = text.format(_format)
            else:
                text = text.format(*_format)


        if colour in ['blue', 'b']: 
            colour = 3447003  # blue
        elif colour in ['red', 'r']: 
            colour = 15158332 # red
        elif colour in ['green', 'g']: 
            colour = 3066993  # green
        elif colour in ['orange', 'o']: 
            colour = 15105570 # orange
        else:
            colour = 0

        embed = discord.Embed(title=embed[0], description=text, colour=colour)

    mess = await channel.send(Message, embed = embed, delete_after = time, components = [[i for i in args]] if args else None)

    if not check:
        return mess

    while True:
        try :event = await client.wait_for('button_click', check = lambda event: event.message == mess, timeout = time)
        except asyncio.TimeoutError:
            event = None
        if await check(event): break


def button(label, style = ButtonStyle.blue, id = 1, disabled = False, url = None):
    return Button(label= label, style=style, id = id, disabled = disabled, url = url)

async def wait_button(client, check, timeout = None):
    mess = check
    if not callable(check):
        def check(event):
            return event.message == mess
                
    try: event = await client.wait_for('button_click', check = check, timeout = timeout)
    except asyncio.TimeoutError:
        return None
    return event

async def respond(event):
    await event.respond(content = language('Du bist nicht berechtigt diesen Knopf zu drücken!', load_guild(event.message.guild).lang))



async def clean_up(client, data = None):
    if not data:
        with open('Data/config.json', 'r') as f:
            data = json.load(f)
        json_int(data)
    vc_list = set()
    chat_list = set()
    for guild_id in data.keys():
        if not isinstance(guild, int):
            continue

        guild = client.get_guild(guild_id)

        if not guild: 
            del data[guild]
            continue
        
        c = load_guild(guild)
        if not c.check():
            pass
            # DO NOTLAGE
        

        for vc_id in c.vc:
            vc_list.add(vc_id)
            chat = c.get_chat(vc_id)
            if chat:
                chat_list.add(chat)
        
        for member in c.members:
            vc_list.add()

            """ if temp and not isinstance(temp, int):
                temp = temp.id

            await asyncio.sleep(1)
            chat = guild.get_channel(temp)
            if chat:
                await chat.delete() """

            c.delete(vc_id)     
def saving():
    while not client: pass
    while True:
        Save_fl = {}
        for i in fl.keys():
            Save_fl[i.id] = [ii.id for ii in fl[i]]
        if Save_fl != {}:
            with open('Data/Friendlist.yaml', 'w') as Friendlist:
                yaml.dump(Save_fl, Friendlist)
        sleep(5)

Thread(target=saving).start()