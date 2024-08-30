// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
use crate::config::*;
use crate::rich_presence::*;


pub async fn main_inner(config: Config) -> ()
{
    let mut discord_bot: serenity::Client; // discord bot


    discord_bot = serenity::Client::builder(&config.DISCORD_BOT_TOKEN, serenity::all::GatewayIntents::default())
        .event_handler(RichPresenceHandler::new(config))
        .await
        .expect("Creating discord bot failed.");


    discord_bot.start().await.expect("Starting discord bot failed."); // start discord bot

    return;
}
