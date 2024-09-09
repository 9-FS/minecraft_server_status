// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
use crate::domain_or_ip::*;


/// # Summary
/// Collection of settings making up the configuration of the application.
#[derive(Clone, Debug, Eq, PartialEq, serde::Deserialize, serde::Serialize)]
#[allow(non_snake_case)]
pub struct Config
{
    pub DISCORD_BOT_TOKEN: String, // discord bot token
    pub MINECRAFT_SERVER_DOMAIN_OR_IP: DomainOrIp, // minecraft server domain or ip, do not add port here
    pub MINECRAFT_SERVER_PORT: Option<u16>, // minecraft server port, optional
    pub REFRESH_INTERVAL: u64, // refresh display every `REFRESH_INTERVAL` seconds
}

impl Default for Config
{
    fn default() -> Self
    {
        Config
        {
            DISCORD_BOT_TOKEN: "".to_owned(),
            MINECRAFT_SERVER_DOMAIN_OR_IP: DomainOrIp::Domain("".to_owned()),
            MINECRAFT_SERVER_PORT: Some(25565),
            REFRESH_INTERVAL: 5,
        }
    }
}