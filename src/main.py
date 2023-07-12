#Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import aiohttp.client_exceptions
import discord, discord.ext.commands, discord.ext.tasks
import ipaddress
import KFS.config, KFS.fstr, KFS.log
import logging
import mcstatus, mcstatus.pinger
import requests
import socket
import time


@KFS.log.timeit
def main() -> None:
    discord_bot: discord.ext.commands.Bot   #discord bot instance
    discord_bot_token: str                  #discord bot token
    intents: discord.Intents                #bot permissions
    REFRESH_FREQUENCY: float=200e-3         #refresh display with 200mHz (every 5s)
    TIMEOUT: int=50                         #internet connection timeout
    
    discord_bot_token=KFS.config.load_config("discord_bot.token")               #load discord bot token
    intents=discord.Intents.default()                                           #standard permissions
    discord_bot=discord.ext.commands.Bot(command_prefix="", intents=intents)    #create bot instance


    @discord_bot.event
    async def on_ready() -> None:
        refresh.start(discord_bot)  #start refresh task, do here so arguments can be passed
        logging.info("Started discord bot.")
        return

    @discord.ext.tasks.loop(seconds=1/REFRESH_FREQUENCY)
    async def refresh(discord_bot: discord.ext.commands.Bot) -> None:    #refresh display regurarily
        """
        refresh bot display
        """
        discord_presence_title: str                                             #presence, important information
        discord_status: discord.Status                                          #current status, online (green) for server online, do not disturb (red) for server offline
        minecraft_server: mcstatus.JavaServer                                   #server instance
        minecraft_server_ip_global: ipaddress.IPv4Address|ipaddress.IPv6Address #target server IP, global
        minecraft_server_ip_user: str                                           #target server IP as defined by user, local or global
        minecraft_server_port: int                                              #target server port
        minecraft_server_status: mcstatus.pinger.PingResponse                   #server status

        minecraft_server_ip_port=KFS.config.load_config("minecraft_server_ip.config").split(":")        #load set server IP/domain and port, may be local or global
        
        minecraft_server_ip_user=minecraft_server_ip_port[0]
        logging.info(f"Converting configured IP \"{minecraft_server_ip_user}\" to global IP...")
        try:
            minecraft_server_ip_global=ipaddress.ip_address(socket.gethostbyname(minecraft_server_ip_user)) #convert to IP
        except socket.gaierror:
            logging.error(f"\rConverting configured IP \"{minecraft_server_ip_user}\" to global IP failed. Unable to get IP address information. Check the given domain/IP and the internet connection.")
            return
        if minecraft_server_ip_global.is_private==True:                                             #if not global IP:
            try:
                minecraft_server_ip_global=ipaddress.ip_address(requests.get("https://ident.me/", timeout=TIMEOUT).text)    #convert to global IP
            except TimeoutError:
                logging.error(f"\rConverting configured IP \"{minecraft_server_ip_user}\" to global IP timed out.")
                return
        logging.info(f"\rConverted configured IP \"{minecraft_server_ip_user}\" to global IP \"{minecraft_server_ip_global.exploded.upper()}\".")
        try:
            minecraft_server_port=int(minecraft_server_ip_port[1])
        except ValueError:
            logging.error(f"Converting given port \"{minecraft_server_ip_port[1]}\" to int failed.")
            return
        
        minecraft_server=mcstatus.JavaServer.lookup(f"{minecraft_server_ip_user}:{minecraft_server_port}")
        logging.info(f"Fetching server status at \"{minecraft_server_ip_user}:{minecraft_server_port}\"...")
        try:
            minecraft_server_status=minecraft_server.status()       #current server status
        except (IOError, TimeoutError):                             #if server currently transitioning between online offline or is currently offline:
            logging.info(f"\rFetching server status at \"{minecraft_server_ip_user}:{minecraft_server_port}\" failed. Server is assumed to be offline.")
            discord_presence_title="offline"                        #just say it's offline
            discord_status=discord.Status.do_not_disturb            #status red
        else:                                                                                                                           #if server online:
            logging.info(f"\rFetched server status at \"{minecraft_server_ip_user}:{minecraft_server_port}\" with latency {KFS.fstr.notation_tech(minecraft_server_status.latency/1000, 2)}s.")
            discord_presence_title=f"{minecraft_server_status.players.online}/{minecraft_server_status.players.max}"                    #player numbers online
            if 1<=minecraft_server_status.players.online:                                                                               #if at least 1 player online:
                discord_presence_title+=f": {', '.join(sorted([player.name for player in minecraft_server_status.players.sample]))}"    #append player name list #type:ignore
            discord_status=discord.Status.online                                                                                        #status green
        discord_presence_title+=f"; IP: {minecraft_server_ip_global.exploded.upper()}:{minecraft_server_port}"
        logging.info(f"Discord bot status: {discord_status}")
        logging.info(f"Presence title: {discord_presence_title}")

        logging.info(f"Applying presence title and bot status...")
        await discord_bot.change_presence(activity=discord.Activity(name=discord_presence_title, type=discord.ActivityType.playing),    #apply presence
                                          status=discord_status,)
        logging.info(f"\rApplied presence title and bot status.")
        return
    

    while True:
        logging.info("Starting discord bot...")
        try:
            discord_bot.run(discord_bot_token)                  #start discord bot now
        except aiohttp.client_exceptions.ClientConnectorError:  #if temporary internet failure: retry connection
            logging.error("Starting discord bot failed, because bot could not connect. Retrying in 10s...")
            time.sleep(10)