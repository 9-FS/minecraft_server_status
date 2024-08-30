# minecraft_server_status
## Introduction

This discord bot queries the minecraft server specified in `./config/.env` `MINECRAFT_SERVER_IP`:`MINECRAFT_SERVER_PORT` and displays the current status of the minecraft server via its rich presence title and bot status. It states either:
- offline, current IP or domain
- current and maximum possible players online, current IP or domain, a player name list should there be any online

## Installation

1. Create a discord application [here](https://discord.com/developers/applications).
    1. Create your bot.
    1. Add it to your server.
    1. Copy your discord bot token.

    If you don't know how to do these steps, I recommend [this tutorial](https://www.writebots.com/discord-bot-token/).
1. Execute the program once. This will create a default `./config/.env`.
1. Fill out the settings. `MINECRAFT_SERVER_PORT` is optional and if you don't want to specifiy one, remove the whole line.