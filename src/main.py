# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import aiohttp.client_exceptions
import discord, discord.ext.commands, discord.ext.tasks
import inspect
import ipaddress
import KFS.config, KFS.fstr, KFS.log
import logging
import mcstatus, mcstatus.pinger
import time
from convert_to_ip_global import convert_to_ip_global


@KFS.log.timeit
def main() -> None:
    discord_bot: discord.ext.commands.Bot   # discord bot instance
    DISCORD_BOT_CHANNEL_NAME: str="botspam" # channel to monitor for ip command
    discord_bot_token: str                  # discord bot token
    intents: discord.Intents                # bot permissions
    REFRESH_FREQUENCY: float=200e-3         # refresh display with 200mHz (every 5s)
    
    discord_bot_token=KFS.config.load_config("discord_bot.token")               # load discord bot token
    intents=discord.Intents.default()                                           # standard permissions
    intents.message_content=True                                                # in addition with message contents
    discord_bot=discord.ext.commands.Bot(command_prefix="", intents=intents)    # create bot instance


    @discord_bot.event
    async def on_ready() -> None:
        refresh.start(discord_bot)  # start refresh task, do here so arguments can be passed
        logging.info("Started discord bot.")
        return

    @discord.ext.tasks.loop(seconds=1/REFRESH_FREQUENCY)
    async def refresh(discord_bot: discord.ext.commands.Bot) -> None:    # refresh display regurarily
        """
        Refreshes bot presence with current number of players online, maximum number of players, player names, and server IP. Also sets status to online or offline as appropiate.
        """

        discord_presence_title: str                                             # presence, important information
        discord_status: discord.Status                                          # current status, online (green) for server online, do not disturb (red) for server offline
        minecraft_server: mcstatus.JavaServer                                   # server instance
        minecraft_server_ip_global: ipaddress.IPv4Address|ipaddress.IPv6Address # target server IP, global
        minecraft_server_ip_user: str                                           # target server IP as defined by user, local or global
        minecraft_server_port: int                                              # target server port
        minecraft_server_status: mcstatus.pinger.PingResponse                   # server status


        minecraft_server_ip_port=KFS.config.load_config("minecraft_server_ip.config").rsplit(":", 1)    # load set server IP/domain and port, may be local or global
        minecraft_server_ip_user=minecraft_server_ip_port[0]
        minecraft_server_ip_global=convert_to_ip_global(minecraft_server_ip_user)
        try:
            minecraft_server_port=int(minecraft_server_ip_port[1])
        except ValueError:
            logging.error(f"Converting given port \"{minecraft_server_ip_port[1]}\" to int failed.")
            return
        

        minecraft_server=mcstatus.JavaServer.lookup(f"{minecraft_server_ip_user}:{minecraft_server_port}")
        logging.info(f"Fetching server status at \"{minecraft_server_ip_user}:{minecraft_server_port}\"...")
        try:
            minecraft_server_status=minecraft_server.status()   # current server status
        except (IOError, TimeoutError):                         # if server currently transitioning between online offline or is currently offline:
            logging.info(f"\rFetching server status at \"{minecraft_server_ip_user}:{minecraft_server_port}\" failed. Server is assumed to be offline.")
            discord_presence_title="offline"                    # just say it's offline
            discord_status=discord.Status.do_not_disturb        # status red
        else:                                                                                                                           # if server online:
            logging.info(f"\rFetched server status at \"{minecraft_server_ip_user}:{minecraft_server_port}\" with latency {KFS.fstr.notation_tech(minecraft_server_status.latency/1000, 2)}s.")
            discord_presence_title=f"{minecraft_server_status.players.online}/{minecraft_server_status.players.max}"                    # player numbers online
            if 1<=minecraft_server_status.players.online:                                                                               # if at least 1 player online:
                discord_presence_title+=f": {', '.join(sorted([player.name for player in minecraft_server_status.players.sample]))}"    # append player name list # type:ignore
            discord_status=discord.Status.online                                                                                        # status green
        discord_presence_title+=f"; IP: {minecraft_server_ip_global.exploded.upper()} :{minecraft_server_port}"                         # display, separate ip and port with space because IPv6 is so long and display needs a linebreak

        logging.info(f"Applying presence title \"{discord_presence_title}\" and bot status \"{discord_status.name}\"...")
        await discord_bot.change_presence(activity=discord.Activity(name=discord_presence_title, type=discord.ActivityType.playing),    # apply presence
                                          status=discord_status,)
        logging.info(f"\rApplied presence title \"{discord_presence_title}\" and bot status \"{discord_status.name}\".")
        return
    

    @discord_bot.event
    async def on_message(message: discord.Message):
        """
        Executed every time a message is sent on the server. If the message is not from the bot itself and in a bot channel, process it.

        - \"ip\" sends the current IP for copy and paste purposes.
        """

        message_send: str                                                       # message to send to discord
        minecraft_server_ip_global: ipaddress.IPv4Address|ipaddress.IPv6Address # target server IP, global
        minecraft_server_ip_user: str                                           # target server IP as defined by user, local or global
        minecraft_server_port: int                                              # target server port

        if(   message.author==discord_bot.user    # if message from bot itself or outside dedicated bot channel or not the right command: do nothing 
           or message.channel.name!=DISCORD_BOT_CHANNEL_NAME    # type:ignore
           or message.content.upper()!="IP"):
            return
        logging.info("Executing IP command...")

        minecraft_server_ip_port=KFS.config.load_config("minecraft_server_ip.config").rsplit(":", 1)    # load set server IP/domain and port, may be local or global
        minecraft_server_ip_user=minecraft_server_ip_port[0]
        minecraft_server_ip_global=convert_to_ip_global(minecraft_server_ip_user)
        try:
            minecraft_server_port=int(minecraft_server_ip_port[1])
        except ValueError:
            logging.error(f"Converting given port \"{minecraft_server_ip_port[1]}\" to int failed.")
            return

        match type(minecraft_server_ip_global): # depending on ip type: output formatting with brackets or without
            case ipaddress.IPv4Address:
                message_send=f"{minecraft_server_ip_global.exploded.upper()}:{minecraft_server_port}"
            case ipaddress.IPv6Address:
                message_send=f"[{minecraft_server_ip_global.exploded.upper()}]:{minecraft_server_port}"
            case _:
                logging.critical(f"minecraft_server_ip_global is of type \"{type(minecraft_server_ip_global)}\" instead of \"ipaddress.IPv4Address\" or \"ipaddress.IPv6Address\".")
                raise RuntimeError(f"Error in {main.__name__}{inspect.signature(main)}: minecraft_server_ip_global is of type \"{type(minecraft_server_ip_global)}\" instead of \"ipaddress.IPv4Address\" or \"ipaddress.IPv6Address\".")
        logging.info(f"Sending message \"{message_send}\" to discord...")
        try:
            await discord_bot.get_channel(message.channel.id).send(message_send)    # send message to discord # type:ignore
        except AttributeError:                                                      # get_channel already returned None, bot has probably been removed from server
            logging.error(f"Sending message \"{message_send}\" to discord failed with AttributeError.")
        except discord.errors.DiscordServerError:                                   # send failed
            logging.error(f"Sending message \"{message_send}\" to discord failed with discord.errors.DiscordServerError.")
        else:
            logging.info(f"\rSent message \"{message_send}\" to discord.")

        return
    

    while True:
        logging.info("Starting discord bot...")
        try:
            discord_bot.run(discord_bot_token)                  # start discord bot now
        except aiohttp.client_exceptions.ClientConnectorError:  # if temporary internet failure: retry connection
            logging.error("Starting discord bot failed, because bot could not connect. Retrying in 10s...")
            time.sleep(10)
        except RuntimeError:
            logging.error("Starting discord bot failed. Retrying in 10s...")
            time.sleep(10)