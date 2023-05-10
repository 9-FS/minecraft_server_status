---
Topic: "Minecraft Server Status for Discord"
Author: "구FS"
---
<link href="./doc_templates/md_style.css" rel="stylesheet"></link>
<body>

# <p style="text-align: center;">Minecraft Server Status for Discord</p>
<br>
<br>

- [1. General](#1-general)
- [2. How to Install](#2-how-to-install)
- [3. Planned Features](#3-planned-features)

## 1. General

This bot loads a minecraft server IP from `minecraft_server_ip.config`, connects to the discord bot with token `discord_bot.token`, and displays the current status of the specified minecraft server via its rich presence title and bot status. It states either:
- offline, current global IP
- current and maximum possible players online, a player name list should there be any online, current global IP

## 2. How to Install

As far as I know, there is currently no way of having rich presences on a per server basis. That's why you can not use this bot by just inviting it to your server. To use this bot:

1. Download the source code or download a release `Minecraft Server Status for Discord.exe`.
1. Copy your discord bot token into `discord_bot.token`.
    1. Create a discord application [here](https://discord.com/developers/applications).
    1. Create your bot.
    1. Add it to your server.
    1. Copy your token into `discord_bot.token`.

   If you don't know how to do these steps, I recommend [this tutorial](https://www.writebots.com/discord-bot-token/).
1. Copy your minecraft server IP with port into `minecraft_server_ip.config`.
1. Execute `main_outer.py` with python or execute the compiled `Metric METAR for Discord.exe`.

<div style="page-break-after: always;"></div>
</body>

## 3. Planned Features

I want to move the current IP and player list into a separate, multiline text field. I think `discord.Activites.details` should be what I'm looking for, but I can't make it work for some reason. Any help would be greatly appreciated!