# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import aiohttp.client_exceptions
import discord, discord.ext.commands, discord.ext.tasks
import dns.exception
import json
from KFSconfig import KFSconfig
from KFSfstr   import KFSfstr
from KFSlog    import KFSlog
import logging
import mcstatus, mcstatus.pinger
import time
from convert_to_ip_public import convert_to_ip_public


@KFSlog.timeit
def main(DEBUG: bool) -> None:
    discord_bot: discord.ext.commands.Bot   # discord bot instance    
    intents: discord.Intents                # bot permissions
    settings: dict                          # settings, loaded from settings.json
    SETTINGS_DEFAULT: str=json.dumps({      # settings default
        "discord_bot_channel_name": "",     # channel to monitor for IP command
        "discord_bot_token": "",            # discord bot token
        "convert_to_ip_public": False,      # if true, convert given server IP or domain to public IP
        "ip_public_version": 4,             # if convert_to_ip_public is true, use IPv4 or IPv6
        "minecraft_server_ip": "",          # minecraft server IP or domain, do not add port here
        "minecraft_server_port": "",        # minecraft server port, may be left empty
        "refresh_frequency": 200e-3,        # refresh display with 200mHz (every 5s)
    }, indent=4)
    

    try:
        settings=json.loads(KFSconfig.load_config("./config/settings.json", SETTINGS_DEFAULT))  # load settings
    except FileNotFoundError:
        return
    if settings["discord_bot_token"]=="":
        logging.critical("discord_bot_token must be set in ./config/settings.json. If you don't know how to do that, refer to: https://www.writebots.com/discord-bot-token/")
        return
    if settings["minecraft_server_ip"]=="":
        logging.critical("minecraft_server_ip must be set in ./config/settings.json.")
        return
    intents=discord.Intents.default()                                           # standard permissions
    intents.message_content=True                                                # in addition with message contents
    discord_bot=discord.ext.commands.Bot(command_prefix="", intents=intents)    # create bot instance


    @discord_bot.event
    async def on_ready() -> None:
        refresh.start(discord_bot)  # start refresh task, do here so arguments can be passed
        logging.info("Started discord bot.")
        return

    @discord.ext.tasks.loop(seconds=1/settings["refresh_frequency"])
    async def refresh(discord_bot: discord.ext.commands.Bot) -> None:    # refresh display regurarily
        """
        Refreshes bot presence with current number of players online, maximum number of players, player names, and server IP. Also sets status to online or offline as appropiate.
        """

        discord_presence_title: str                             # presence, important information
        discord_status: discord.Status                          # current status, online (green) for server online, do not disturb (red) for server offline
        minecraft_server: mcstatus.JavaServer                   # server instance
        minecraft_server_display_ip_port: str                   # server IP and if set port, may be IP or domain given or public IP
        minecraft_server_ip_port: str                           # target server IP and if set port, may be IP or domain given or public IP
        minecraft_server_status: mcstatus.pinger.PingResponse   # server status
        LOOKUP_TIMEOUT: float=5                                 # timeout for server lookup in seconds

        
        minecraft_server_ip_port=settings["minecraft_server_ip"]
        if settings["minecraft_server_port"]!="":   # if port given in settings:
            minecraft_server_ip_port+=f":{settings['minecraft_server_port']}"

        logging.info(f"Looking up \"{minecraft_server_ip_port}\"...")
        try:
            minecraft_server=mcstatus.JavaServer.lookup(minecraft_server_ip_port, timeout=LOOKUP_TIMEOUT)   # lookup server with IP or domain given
        except dns.exception.Timeout:                                                                       # resolving DNS timed out, DNS server may have a failure
            logging.info(f"\rLooking up DNS \"{minecraft_server_ip_port}\" timed out. Server status is unknown.")
            discord_presence_title="unknown"                                                                # say it's unknown
            discord_status=discord.Status.idle                                                              # status yellow
        except TimeoutError:
            logging.info(f"\rLooking up \"{minecraft_server_ip_port}\" failed. Server is assumed to be offline.")
            discord_presence_title="offline"                                                                # just say it's offline
            discord_status=discord.Status.do_not_disturb                                                    # status red
        
        else:
            logging.info(f"\rLooked up \"{minecraft_server_ip_port}\".")
            logging.info(f"Fetching server status at \"{minecraft_server_ip_port}\"...")
            try:
                minecraft_server_status=minecraft_server.status()                                                                                           # current server status
            except (IOError, TimeoutError):                                                                                                                 # if server currently transitioning between online offline or is currently offline:
                logging.info(f"\rFetching server status at \"{minecraft_server_ip_port}\" failed. Server is assumed to be offline.")
                discord_presence_title="offline"                                                                                                            # just say it's offline
                discord_status=discord.Status.do_not_disturb                                                                                                # status red
            else:                                                                                                                                           # if server online:
                logging.info(f"\rFetched server status at \"{minecraft_server_ip_port}\" with latency {KFSfstr.notation_tech(minecraft_server_status.latency/1000, 2)}s.")
                discord_presence_title=f"{minecraft_server_status.players.online}/{minecraft_server_status.players.max}"                                    # player numbers online
                if 1<=minecraft_server_status.players.online:                                                                                               # if at least 1 player online:
                    discord_presence_title+=f": {', '.join(sorted([player.name for player in minecraft_server_status.players.sample], key=str.casefold))}"  # append player name list, sort case insensitive # type:ignore
                discord_status=discord.Status.online                                                                                                        # status green
        

        if settings["convert_to_ip_public"]==True:                                      # if convert to public IP: convert
            minecraft_server_display_ip_port=convert_to_ip_public(settings["minecraft_server_ip"], settings["ip_public_version"])
        else:                                                                           # else: use given IP or domain
            minecraft_server_display_ip_port=settings["minecraft_server_ip"]
        if settings["minecraft_server_port"]!="":                                       # if port given in settings:
            minecraft_server_display_ip_port+=f": {settings['minecraft_server_port']}"  # append port, space before port for linebreak
        discord_presence_title+=f"; IP: {minecraft_server_display_ip_port}"             # append IP

        logging.info(f"Applying presence title \"{discord_presence_title}\" and bot status \"{discord_status.name}\"...")
        try:
            await discord_bot.change_presence(activity=discord.Activity(name=discord_presence_title, type=discord.ActivityType.playing),    # apply presence
                                            status=discord_status,)
        except aiohttp.client_exceptions.ClientConnectorError as e:                                                                         # if internet connection fails
            logging.error(f"\rApplying presence title \"{discord_presence_title}\" and bot status \"{discord_status.name}\" failed with {KFSfstr.full_class_name(e)}. Error: {e.args}")
        else:
            logging.info(f"\rApplied presence title \"{discord_presence_title}\" and bot status \"{discord_status.name}\".")
        return
    

    @discord_bot.event
    async def on_message(message: discord.Message):
        """
        Executed every time a message is sent on the server. If the message is not from the bot itself and in a bot channel, process it.

        - \"ip\" sends the current IP for copy and paste purposes.
        """

        message_send: str   # message to send to discord


        if(   message.author==discord_bot.user  # if message from bot itself or outside dedicated bot channel or not the right command: do nothing 
           or message.channel.name!=settings["discord_bot_channel_name"]    # type:ignore
           or message.content.casefold()!="ip"):
            return
        

        logging.info("Executing IP command...")
        if settings["convert_to_ip_public"]==True:  # if convert to public IP: convert
            message_send=convert_to_ip_public(settings["minecraft_server_ip"], settings["ip_public_version"])
        else:                                       # else: use IP or domain given
            message_send=settings["minecraft_server_ip"]
        if settings["minecraft_server_port"]!="":   # if port given in settings:
            message_send+=f":{settings['minecraft_server_port']}"

        logging.info(f"Sending message \"{message_send}\" to discord...")
        try:
            await discord_bot.get_channel(message.channel.id).send(message_send)                                            # send message to discord # type:ignore
        except (aiohttp.client_exceptions.ClientConnectorError, AttributeError, discord.errors.DiscordServerError) as e:    # if internet connection fails; get_channel already returned None, bot has probably been removed from server; send failed
            logging.error(f"Sending message \"{message_send}\" to discord failed with {KFSfstr.full_class_name(e)}. Error: {e.args}")
        else:
            logging.info(f"\rSent message \"{message_send}\" to discord.")

        return
    

    while True:
        logging.info("Starting discord bot...")
        try:
            discord_bot.run(settings["discord_bot_token"])                          # start discord bot now
        except (aiohttp.client_exceptions.ClientConnectorError, RuntimeError) as e: # if internet connection fails: retry connection
            logging.error(f"Starting discord bot failed with {KFSfstr.full_class_name(e)}. Error: {e.args}\nRetrying in 10s...")
            time.sleep(10)