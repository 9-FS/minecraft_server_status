#Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import aiohttp.client_exceptions
import discord, discord.ext.commands, discord.ext.tasks
import KFS.config, KFS.log
import logging
import mcstatus, mcstatus.pinger
import time


@KFS.log.timeit
def main() -> None:
    discord_bot: discord.ext.commands.Bot   #discord bot instance
    discord_bot_token: str                  #discord bot token
    intents: discord.Intents                #bot permissions
    minecraft_server: mcstatus.JavaServer   #server instance
    minecraft_server_ip: str                #target server IP
    REFRESH_FREQUENCY: float=200e-3         #refresh display with 200mHz (every 5s)
    
    discord_bot_token=KFS.config.load_config("discord_bot.token")               #load discord bot token
    intents=discord.Intents.default()                                           #standard permissions
    discord_bot=discord.ext.commands.Bot(command_prefix="", intents=intents)    #create bot instance
    minecraft_server_ip=KFS.config.load_config("minecraft_server_ip.config")    #load server IP
    minecraft_server=mcstatus.JavaServer.lookup(minecraft_server_ip)


    @discord_bot.event
    async def on_ready() -> None:
        refresh.start(discord_bot, minecraft_server)    #start refresh task, do here so arguments can be passed
        logging.info("Started discord bot.")
        return

    @discord.ext.tasks.loop(seconds=1/REFRESH_FREQUENCY)
    async def refresh(discord_bot: discord.ext.commands.Bot, minecraft_server: mcstatus.JavaServer) -> None:    #refresh display regurarily
        """
        refresh bot display
        """
        discord_presence_title: str                             #presence, important information
        minecraft_server_status: mcstatus.pinger.PingResponse   #server status
        

        try:
            minecraft_server_status=minecraft_server.status()   #current server status
        except (IOError, TimeoutError):                         #if server currently transitioning between online offline or is currently offline:
            discord_presence_title="server offline"             #just say it's offline
            await discord_bot.change_presence(activity=discord.Activity(name=discord_presence_title, type=discord.ActivityType.playing),
                                              status=discord.Status.do_not_disturb,)
            return
        
        discord_presence_title=f"{minecraft_server_status.players.online}/{minecraft_server_status.players.max} playing"    #default title
        if 0<minecraft_server_status.players.online:                                                                        #if at least 1 player online: append player name list
            discord_presence_title+=f": {', '.join(sorted([player.name for player in minecraft_server_status.players.sample]))}"    #type:ignore
        await discord_bot.change_presence(activity=discord.Activity(name=discord_presence_title, type=discord.ActivityType.playing),
                                          status=discord.Status.online,)
        return
    

    while True:
        logging.info("Starting discord bot...")
        try:
            discord_bot.run(discord_bot_token)                  #start discord bot now
        except aiohttp.client_exceptions.ClientConnectorError:  #if temporary internet failure: retry connection
            logging.error("Starting discord bot failed, because bot could not connect. Retrying in 10s...")
            time.sleep(10)