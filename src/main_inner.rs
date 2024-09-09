// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
use crate::config::*;
use crate::error::*;
use crate::rich_presence::*;


pub async fn main_inner(config: Config) -> Result<()>
{
    let mut discord_bot: serenity::Client; // discord bot


    match serenity::Client::builder(&config.DISCORD_BOT_TOKEN, serenity::all::GatewayIntents::default())
        .event_handler(RichPresenceHandler::new(config.clone()))
        .await
    {
        Ok(o) => discord_bot = o, // created discord bot successfully
        Err(e) => {return Err(Error::SettingInvalid { name: "DISCORD_BOT_TOKEN".to_owned(), value: config.DISCORD_BOT_TOKEN, reason: e.to_string()});} // creating discord bot failed
    }


    discord_bot.start().await?; // start discord bot

    return Ok(());
}