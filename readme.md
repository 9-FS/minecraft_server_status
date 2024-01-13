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

## 1. General

This discord bot queries the minecraft server specified in "./config/settings.json" `minecraft_server_ip`:`minecraft_server_port` and displays the current status of the minecraft server via its rich presence title and bot status. It states either:
- offline, current IP or domain
- current and maximum possible players online, a player name list should there be any online, current IP or domain

By default, it just displays the given IP or domain. If `convert_to_ip_global` is set to `true`, it will convert the given domain or IP to a public IP for its display. This is useful if you are hosting your server on a local machine and want to display the public IP of your router. Be advised that the given IP or domain in `minecraft_server_ip` will still be used for the query. If you convert the given IP or domain to a public IP, you can choose the preferred IP version with `ip_public_version`. This version is not guaranteed though and will fallback to another version if the preferred version is not available with "https://{ip_public_version}.ident.me/". `minecraft_server_port` can be used to manually specify the port, but it can also be left empty and will default to 25565.

You can specify a bot channel with `discord_bot_channel_name`. If you write "ip" into that channel, the bot will answer with the current display IP or domain for easy copy and paste.

## 2. How to Install

As far as I know, there is currently no way of having rich presences on a per server basis. That's why you can not use this bot by just inviting it to your server. To use this bot:

1. Download the source code or download a release `Minecraft Server Status for Discord.exe`.
1. Copy your discord bot token into "./config/settings.json" `discord_bot_token`.
    1. Create a discord application [here](https://discord.com/developers/applications).
    1. Create your bot.
    1. Add it to your server.
    1. Copy your token into `discord_bot.token`.

   If you don't know how to do these steps, I recommend [this tutorial](https://www.writebots.com/discord-bot-token/).
1. Copy your minecraft server IP or domain into "./config/settings.json" `minecraft_server_ip`.
1. Execute `main_outer.py` with python or execute the compiled program.

<div style="page-break-after: always;"></div>
</body>