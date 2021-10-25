import json
from os import system

import discord
import yaml
from discord.ext import commands
from discord_components import *
from VoiceModule import *


class newServer(commands.Cog):
    def __init__(self, client):
        self.client = client
        DiscordComponents(self.client)
        
    @commands.Cog.listener()
    async def on_ready(self):
        with open('Data/config.json', 'r') as f:
            self.config = json.load(f)
            if not self.config:
                self.config = {}
        with open('Data/LanguesForm.yml') as f:
            self.langformat = yaml.load(f, Loader = yaml.FullLoader)
        print('Module >>> newServer')  

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        botchannel = await guild.create_text_channel('VoiceTime-Bot')
        await botchannel.set_permissions(guild.default_role, view_channel = False)
        self.config[guild.id] = {"lang" : None,
                                 "Finish" : False,
                                 "channel" : 
                                 {  
                                     'Normal' : None,
                                     'Privat' : None,
                                     'Voice-Setting' : None,
                                     'Voice-Logs' : None,
                                     'Queue' : None,
                                     'pub-logs' : None, 
                                     'config' : botchannel.id,
                                 }
                                }
        
        self.restart(self, guild)

    @commands.command()
    async def ping(self,ctx):
        guild = ctx.guild
        botchannel = await guild.create_text_channel('VoiceTime-Bot')
        await botchannel.set_permissions(guild.default_role, view_channel = False)
        config_channel = botchannel.id
        await self.restart(guild, config_channel)


    @commands.command()
    async def restart(self, par, cc = None):    # sourcery no-metrics
        if isinstance(par, commands.Context):
            guild = par.guild
            #if not self.config[guild.id].get('Finish'): 
            #    return await par.send(embed=embed('Error', 'You need to finish the configuration before you can use this command.', 'r'))
        else: guild = par   
        
        auto = False

        botchannel = guild.get_channel(cc)
        if not botchannel:
            botchannel = await guild.create_text_channel('VoiceTime-Bot')
            await botchannel.set_permissions(guild.default_role, view_channel = False)

        config = {}
        
        mess = await botchannel.send(embed = embed('Configuration', "Please select a language!"),
                              components = [[Button(label = "de", style=ButtonStyle.blue, id = 'de'),
                                             Button(label = "en", style=ButtonStyle.blue, id = 'en'),
                              ]])
        
        event = await self.client.wait_for("button_click", check = lambda event: event.message == mess)
        await event.respond(type=6)
        await mess.edit(components = [[Button(label = "de", style=ButtonStyle.blue, disabled= True),
                                      Button(label = "en", style=ButtonStyle.blue, disabled= True)]])
        
        lang = event.component.id
        config['Langues'] = lang 

        l = lambda text: language(text, lang)
        def info(t): return embed('**INFO**', t, 'o')
        def conf(t): return embed(l('Konfiguration'), t)
        await botchannel.send(embed=embed(l('Konfiguration'), l('Die Sprache wurde auf {} umgestellt').format(self.langformat[lang])))
        await botchannel.send(embed=info('Wenn du die Sprache um ändern möchtest, führe den Command **//set lang** aus'))
        mess = await botchannel.send(embed=embed(l('Konfiguration'), l('Willst du den Server automatich konfigurieren oder manuel?')),
            components = [[Button(label = l('automatisch'), style = ButtonStyle.blue, id = 'a'),
                           Button(label = l('manuel'), style = ButtonStyle.blue, id = 'm')]])

        event = await self.client.wait_for("button_click", check = lambda event: event.message == mess)
        await event.respond(type=6)
        await mess.edit(components = [[Button(label = l('automatisch'), style=ButtonStyle.blue, disabled= True),
                                      Button(label = l('manuel'), style=ButtonStyle.blue, disabled= True)]])
        user = event.user
        await botchannel.send(embed=embed(l('Kanal Übersicht'), l('**Voice-Setting** \n> Hier wird der erstelle Voice-Channel eingestellt\n**voice-logs**\n> Hier werden die Logs vom Voice Channel gespeichert\n **Talk** \n> Hier wird der normale Sprachchat erstellt \n **private Talk** \n> Hier wird der private Sprachchat erstellt'))) 
        
        if event.component.id == 'a':
            auto = True
            mess = await botchannel.send(embed=embed(l('Konfiguration'), l(
            "Erstelle Kategorie *Voice-Text*\n> Erstelle *Voice-Setting*\n> Erstelle *Voice-Logs*\nErstelle Kategorie *Voice-Channel*\n> Erstelle *>>> Talk*\n> Erstelle *>>> privat Talk*"
            )))


            cate1 = await guild.create_category('Voice-Config')
            await cate1.set_permissions(guild.default_role, view_channel = False)
            v1 = await guild.create_text_channel('Voice-Setting', category=cate1)
            v2 = await guild.create_text_channel('Voice-Logs', category=cate1)
            cate2 = await guild.create_category('VoiceChat')
            await cate2.set_permissions(guild.default_role, view_channel = False)
            v3 = await guild.create_voice_channel('>>> Talk', category=cate2)
            v4 = await guild.create_voice_channel('>>> private Talk', category=cate2)

            config['Normal_Channel'] = v3.id
            config['Privat_Channel'] = v4.id
            config['Voice_Setting_Chat'] = v1.id
            config['Voice_Logs_Chat'] = v2.id
            config['Queue'] = None
            config['Voice_Logs_Public'] = True
            


            await botchannel.send(embed=embed(l('**INFO**'), l('Du kannst jeden, vom Bot erstellten, Kanal umbenennen und verschieben!'), 'o'))

            await mess.edit(embed=embed(l('Konfiguration'), l(
            "Kategorie {} wurde erstellt\n> {} wurde erstellt\n> {} wurde erstellt\nKategorie {} wurde erstellt\n> {} wurde erstellt\n> {} wurde erstellt"
            ).format('Voice-Config', v1.mention, v2.mention, 'VoiceChat', v3.mention, v4.mention)))
        
        else:
            await botchannel.send(embed=embed(l('**INFO**'), l('Du kannst jeden, vom Bot erstellten, Kanal umbenennen und verschieben!'), 'o'))
                
            for i in ['Normal', 'Privat']:
                exist = None
                mess = await botchannel.send(embed=embed(l('Konfiguration'), l('**__{} Talk__** \nBitte trete den Channel bei der der **{} Talk** sein soll').format(i,i)))
                
                while True:
                    _,__,channel = await self.client.wait_for('voice_state_update', check = lambda x,_,a: x == user and a)
                    channel = channel.channel
                    if channel.id == config.get('Normal_Channel'):
                        await botchannel.send(embed=embed(l('Normal Talk und Privat Talk dürfen nicht den gleichen Channel haben!')), delete_after = 5)
                        continue
                    if not exist:
                        check_mess = await botchannel.send(embed=embed(l('Bestätigung'), l('Bist du dir sicher das {} der neue **{} Talk** Channel ist?').format(channel.mention, i)),
                            components = [[Button(label = l('Ja'), style = ButtonStyle.blue, id = 'True'),Button(label = l('Nein'), style = ButtonStyle.red, id = 'False')]])       
                        exist = True
                    else:
                        await check_mess.edit(embed=embed(l('Bestätigung'), l('Bist du dir sicher das {} der neue **{} Talk** Channel ist?').format(channel.mention, i)),
                            components = [[Button(label = l('Ja'), style = ButtonStyle.blue, id = 'True'),Button(label = l('Nein'), style = ButtonStyle.red, id = 'False')]])

                    event = await self.client.wait_for('button_click', check = lambda x:x.message == check_mess and x.user == user)
                    await event.respond(type=6)

                    if event.component.id == 'True':
                        await check_mess.delete()
                        await mess.delete()
                        if i == 'Normal':
                            config['Normal_Channel'] = channel.id
                            channel_overview = await botchannel.send(embed=embed(l('Kanäle'), l("""
                            normal Talk   >>> {}
                            privat Talk   >>> ...
                            Voice-Setting >>> ...
                            Voice-Logs    >>> ...                           
                            """).format(channel.mention)))
                        else:
                            config['Privat_Channel'] = channel.id
                            await channel_overview.edit(embed=embed(l('Kanäle'), l("""
                            normal Talk   >>> {}
                            privat Talk   >>> {}
                            Voice-Setting >>> ...
                            Voice-Logs    >>> ...                           
                            """).format(guild.get_channel(config['Normal_Channel']).mention, channel.mention)))
                        break
                    
                    await check_mess.edit(embed=conf(l('Wartet auf {}, das er einen Sprach Chat beitretet!').format(user.mention)),
                    components = [[Button(label = l('Ja'), style = ButtonStyle.grey, disabled=True),Button(label = l('Nein'), style = ButtonStyle.grey, disabled=True)]]) 
            
            # Wartschlange Anfrage
            mess10 = await botchannel.send(embed=conf(l('Willst du den Voice Channel **Warteschlange** hinzufügen?')),
                components = [[Button(label = l('Ja'), style = ButtonStyle.blue, id = 'True'),Button(label = l('Nein'), style = ButtonStyle.red, id = 'False')]])      

            event = await self.client.wait_for('button_click', check = lambda x: x.message == mess10 and x.user == user)
            await event.respond(type = 6)

            # Wartschlange Erstellen
            if event.component.id == 'True':
                exist = False
                await mess10.delete() 
                mess = await botchannel.send(embed=conf(l('**__Warteschlange__** \nBitte trete den Channel bei der der **Warteschlange Talk** sein soll')))

                while True:
                    # Channel auswählen 
                    _,__,channel = await self.client.wait_for('voice_state_update', check = lambda x,_,a: x == user and a)
                    channel = channel.channel

                    # Error: Same Channel
                    if channel.id == config.get('Normal_Channel'):
                        await botchannel.send(embed=embed(l('Wartschlange und Normal Talk dürfen nicht den gleichen Channel haben!')), delete_after = 5)
                        continue
                    elif channel.id == config.get('Privat_Channel'):
                        await botchannel.send(embed=embed(l('Wartschlange und Privat Talk dürfen nicht den gleichen Channel haben!')), delete_after = 5)
                        continue
                    
                    # Bestätigung (Warteschlange) 
                    if not exist:
                        check_mess = await botchannel.send(embed=embed(l('Bestätigung'), l('Bist du dir sicher das {} der neue **{}** Channel ist?').format(channel.mention, l('Warteschlange'))),
                            components = [[Button(label = l('Ja'), style = ButtonStyle.blue, id = 'True'),Button(label = l('Nein'), style = ButtonStyle.red, id = 'False')]])       
                        exist = True
                    else:
                        await check_mess.edit(embed=embed(l('Bestätigung'), l('Bist du dir sicher das {} der neue **{}** Channel ist?').format(channel.mention, l('Warteschlange'))),
                            components = [[Button(label = l('Ja'), style = ButtonStyle.blue, id = 'True'),Button(label = l('Nein'), style = ButtonStyle.red, id = 'False')]])

                    event = await self.client.wait_for('button_click', check = lambda x:x.message == check_mess and x.user == user)
                    await event.respond(type=6)
                    
                    # Save (Warteschlange)
                    if event.component.id == 'True':
                        Warteschlange = l('\nWarteschlange >>> {}').format(channel.mention)
                        config['Warteschlange'] = channel.id
                        await check_mess.delete()
                        await mess.delete()

                        await channel_overview.edit(embed=embed(l('Kanäle'), l("""
                        normal Talk   >>> {}
                        privat Talk   >>> {}
                        Warteschlange >>> {}
                        Voice-Setting >>> ...
                        Voice-Logs    >>> ...                           
                        """).format(guild.get_channel(config['Normal_Channel']).mention,guild.get_channel(config['Privat_Channel']).mention, channel.mention)))
                        break
                    
                    # EXTRA
                    await check_mess.edit(embed=conf(l('Wartet auf {}, das er einen Sprach Chat beitretet!').format(user.mention)),
                    components = [[Button(label = l('Ja'), style = ButtonStyle.grey, disabled=True),Button(label = l('Nein'), style = ButtonStyle.grey, disabled=True)]]) 
            else:
                await mess10.delete()
                Warteschlange = ' '


            # TEXT CHANNEL erstellen 
            for i in ['Voice-Setting', 'Voice-Logs']:
                exist = None
                mess = await botchannel.send(embed=conf(l('__**{}**__\n Bitte schreibe "SELECT" in channel der **{}** sein soll.').format(i,i)))


                # TEXT CHANNEL auswählen
                while True:
                    temp_ctx = await self.client.wait_for('message', check = lambda x: x.author == user and x.content.lower() == "select") 
                    channel = temp_ctx.channel

                    # Error: Same Channel
                    if channel.id == config.get('Voice_Setting_Chat'):
                        await botchannel.send(embed=embed(l('Voice-Setting und Voice-logs dürfen nicht den gleichen Channel haben!')), delete_after = 5)
                        continue

                    # Bestätigung (Text Channel)
                    if not exist:
                        check_mess = await botchannel.send(embed=embed(l('Bestätigung'), l('Bist du dir sicher das {} der neue **{}** Channel ist?').format(channel.mention, i)),
                            components = [[Button(label = l('Ja'), style = ButtonStyle.blue, id = 'True'), Button(label = l('Nein'), style = ButtonStyle.red, id = 'False')]])       
                        exist = True
                    else:
                        await check_mess.edit(embed=embed(l('Bestätigung'), l('Bist du dir sicher das {} der neue **{}* Channel ist?').format(channel.mention, i)),
                            components = [[Button(label = l('Ja'), style = ButtonStyle.blue, id = 'True'), Button(label = l('Nein'), style = ButtonStyle.red, id = 'False')]])

                    event = await self.client.wait_for('button_click', check = lambda x:x.message == check_mess and x.user == user)
                    await event.respond(type=6)

                    # Save (Text Channel) 
                    if event.component.id == 'True':
                        await check_mess.delete()
                        await mess.delete()
                        if i == 'Voice-Setting':
                            config['Voice_Setting_Chat'] = channel.id
                            await channel_overview.edit(embed=embed(l('Kanäle'), l("""
                            normal Talk   >>> {}
                            privat Talk   >>> {}{}
                            Voice-Setting >>> {}
                            Voice-Logs    >>> ...                           
                            """).format(guild.get_channel(config['Normal_Channel']).mention,guild.get_channel(config['Privat_Channel']).mention, Warteschlange, channel.mention)))
                        else:
                            config['Voice_Logs_Chat'] = channel.id
                            # PUBLIC PRIVATE Voice-Logs
                            public = await botchannel.send(embed=conf(l('Soll der Voice-Logs Channel Öffentlich oder Privat sein?')),
                                components = [[Button(label = l('Öffentlich'), style = ButtonStyle.blue, id = 'public'), 
                                              Button(label = l('Privat'), style = ButtonStyle.red)]])

                            event = await self.client.wait_for('button_click', check = lambda x: x.message == public and x.user == user)

                            if event.component.id == 'public':
                                await channel.set_permissions(guild.default_role, view_channel = True)
                                config['Voice_Logs_Public'] = True
                            else:
                                await channel.set_permissions(guild.default_role, view_channel = False)
                                config['Voice_Logs_Public'] = False
                            
                            await public.delete()

                            await channel_overview.edit(embed=embed(l('Kanäle'), l("""
                            normal Talk   >>> {}
                            privat Talk   >>> {}{}
                            Voice-Setting >>> {}
                            Voice-Logs    >>> {}                           
                            """).format(guild.get_channel(config['Normal_Channel']).mention, guild.get_channel(config['Privat_Channel']).mention, Warteschlange, guild.get_channel(config['Voice_Setting_Chat']).mention, channel.mention)))
                        break
                    
                    # EXTRA
                    await check_mess.edit(embed=conf(l('Wartet auf {}, das er einem Text Channel "SELECT" schreibt!').format(user.mention)),
                    components = [[Button(label = l('Ja'), style = ButtonStyle.grey, disabled=True),Button(label = l('Nein'), style = ButtonStyle.grey, disabled=True)]])            

            
        # SAVE ALL

        if 'voice' not in self.config.keys():
            config['voice'] = {'member' : {}, 'vc' : {},'chat' : {}}
            config['friends'] = {}
        
        config['Config'] = botchannel.id
        self.config[str(guild.id)] = config
        # CONFIG = {guild.id : config}
        lastmess = await botchannel.send(embed = conf(l('Die Einstellungen werden gespeichert!')))
        with open('Data/config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
        
        if auto:
            await cate1.set_permissions(guild.default_role, view_channel = True)
            await cate2.set_permissions(guild.default_role, view_channel = True)
            await v1.set_permissions(guild.default_role, view_channel = True)
            await v2.set_permissions(guild.default_role, view_channel = True)
            await v3.set_permissions(guild.default_role, view_channel = True)
            await v4.set_permissions(guild.default_role, view_channel = True)
        else:
            print(auto)
        # Finish
        await lastmess.edit(embed = conf(l('Der Bot ist fertig Eingerichtet! \nSie können nun den Channel als Verwaltung Channel für diesen Bot benutzen oder löschen!')))

        await botchannel.send(embed = info(l('Wenn du den Server neu einrichten willst dann mache **//restart**')))
            




def setup(client):
    client.add_cog(newServer(client))
