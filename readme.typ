#import "@preview/wrap-it:0.1.0": wrap-content  // https://github.com/ntjess/wrap-it/blob/main/docs/manual.pdf
#import "./doc_templates/src/style.typ": set_style
#import "./doc_templates/src/note.typ": *


#show: doc => set_style(
    topic: "Minecraft Server Status for Discord",
    author: "구FS",
    language: "EN",
    doc
)


#align(center, text(size: 8mm, weight: "bold")[Minecraft Server Status for Discord])
#line(length: 100%, stroke: 0.3mm)
\
\
= Introduction

This discord bot queries the minecraft server specified in `./config/settings.json` `MINECRAFT_SERVER_IP`:`MINECRAFT_SERVER_PORT` and displays the current status of the minecraft server via its rich presence title and bot status. It states either:
- offline, current IP or domain
- current and maximum possible players online, a player name list should there be any online, current IP or domain

= Table of Contents

#outline()

#pagebreak(weak: true)

= Installation

By default, it just displays the given IP or domain. If `CONVERT_TO_IP_PUBLIC` is set to `true`, it will convert the given domain or IP to a public IP for its display. This is useful if you are hosting your server on a local machine and want to display the public IP of your router. Be advised that the given IP or domain in `MINECRAFT_SERVER_IP` will still be used for the query. If you convert the given IP or domain to a public IP, you can choose the preferred IP version with `IP_PUBLIC_VERSION`. This version is not guaranteed though and will fallback to another version if the preferred version is not available with #link("https://{IP_PUBLIC_VERSION}.ident.me/"). `MINECRAFT_SERVER_PORT` can be used to manually specify the port, but can also be left empty and will default to 25565.

You can specify a bot channel with `discord_bot_channel_name`. If you write "ip" into that channel, the bot will answer with the current display IP or domain for easy copy and paste.