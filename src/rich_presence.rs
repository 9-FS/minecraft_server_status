// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
use crate::config::*;
use crate::domain_or_ip::*;


pub struct RichPresenceHandler
{
    config: Config, // holds config
}

impl RichPresenceHandler
{
    pub fn new(config: Config) -> Self
    {
        return RichPresenceHandler { config: config };
    }
}

#[serenity::async_trait]
impl serenity::all::EventHandler for RichPresenceHandler
{
    async fn ready(&self, ctx: serenity::all::Context, _: serenity::all::Ready) -> () // when bot is ready
    {
        tokio::spawn(manage_rich_presence(
            ctx,
            self.config.MINECRAFT_SERVER_DOMAIN_OR_IP.clone(),
            self.config.MINECRAFT_SERVER_PORT,
            self.config.REFRESH_INTERVAL,
        )); // spawn task to manage rich presence

        return;
    }
}


/// # Summary
/// Tries to connect to minecraft server at "{mc_server_domain_or_ip}:{mc_server_port}" and updates discord rich presence with the results every `refresh_interval` seconds.
///
/// # Arguments
/// - `ctx`: discord bot context
/// - `mc_server_domain_or_ip`:  minecraft server domain or ip
/// - `mc_server_port`: minecraft server port, optional
async fn manage_rich_presence(ctx: serenity::all::Context, mc_server_domain_or_ip: DomainOrIp, mc_server_port: Option<u16>, refresh_interval: u64) -> !
{
    let mut discord_presence_title: String; // discord rich presence, ip address or domain and list of online players
    let mut discord_status: serenity::model::user::OnlineStatus; // discord bot status, online, offline, etc.
    let mc_server_address: String; // full domain or ip and optionally port, for logging and display


    mc_server_address = match mc_server_port
    {
        Some(port) => format!("{}:{}", String::from(mc_server_domain_or_ip.clone()), port),
        None => String::from(mc_server_domain_or_ip.clone()),
    };


    loop
    {
        match generate_rich_presence(mc_server_domain_or_ip.clone(), mc_server_port, mc_server_address.as_str()).await
        // refresh rich presence
        {
            Ok(o)=>
            {
                discord_status = o.0; // set status
                discord_presence_title = o.1; // set rich presence
            }
            Err(e) =>
            {
                log::error!("{e}"); // log error
                log::info!("Server is assumed to be offline.");
                discord_status = serenity::model::user::OnlineStatus::DoNotDisturb; // set status do not disturb (red), means offline
                discord_presence_title = format!("offline; IP: {mc_server_address}"); // set offline message
            }
        }

        log::info!("Applying presence title \"{}\" and bot status \"{:?}\"...", discord_presence_title, discord_status);
        ctx.set_presence(Some(serenity::all::ActivityData::custom(discord_presence_title.clone())), discord_status); // set discord bot status
        log::info!("\rApplied presence title \"{}\" and bot status \"{:?}\".", discord_presence_title, discord_status);

        tokio::time::sleep(std::time::Duration::from_secs(refresh_interval)).await;
        // sleep for interval seconds
    }
}


/// # Summary
/// Tries to fetch data from minecraft server and generates corresponding discord bot status and discord rich presence.
///
/// # Arguments
/// - `mc_server_domain_or_ip`: domain or ip of minecraft server
/// - `mc_server_port`: port of minecraft server, optional
/// - `mc_server_address`: full domain or ip and optionally port, for logging and display
///
/// # Returns
/// - `Ok((discord_status, discord_rich_presence))`: discord bot status and discord rich presence
/// - `Err(e)`: error
async fn generate_rich_presence(
    mc_server_domain_or_ip: DomainOrIp,
    mc_server_port: Option<u16>,
    mc_server_address: &str,
) -> Result<(serenity::model::user::OnlineStatus, String), async_minecraft_ping::ServerError>
{
    let mut discord_rich_presence: String; // discord rich presence, ip address or domain and list of online players
    let discord_status: serenity::model::user::OnlineStatus; // discord bot status, online, offline, etc.
    let f = scaler::Formatter::new() // formatter
        .set_scaling(scaler::Scaling::None)
        .set_rounding(scaler::Rounding::Magnitude(0));
    let mut mc_server_config: async_minecraft_ping::ConnectionConfig; // minecraft server
    let mut player_names: Vec<String>; // list of online player names


    mc_server_config = async_minecraft_ping::ConnectionConfig::build(mc_server_domain_or_ip); // set domain or ip
    if let Some(port) = mc_server_port
    // if port given: set
    {
        mc_server_config = mc_server_config.with_port(port);
    }

    log::info!("Connecting to minecraft server at {mc_server_address}...");
    let mc_server: async_minecraft_ping::StatusConnection = mc_server_config.connect().await?; // connect to server, ConnectionConfig -> StatusConnection
    log::info!("\rConnected to minecraft server at {mc_server_address}.");

    log::info!("Fetching status from minecraft server at {mc_server_address}...");
    let mc_server = mc_server.status().await?; // request data, StatusConnection -> PingConnection
    log::info!("\rFetched status from minecraft server at {mc_server_address}.");

    discord_status = serenity::model::user::OnlineStatus::Online; // set status online

    discord_rich_presence = format!("{}/{}; {mc_server_address}", f.format(mc_server.status.players.online), f.format(mc_server.status.players.max)); // set online presence
    if 1 <= mc_server.status.players.online
    // if players online: add player list
    {
        player_names = mc_server.status.players.sample.unwrap_or_default().iter().map(|player| player.name.clone()).collect(); // get player names
        player_names.sort_by_key(|player_name| player_name.to_lowercase()); // sort player names case insensitive
        discord_rich_presence += format!(": {}", player_names.join(",").as_str()).as_str();
        // collapse player name list into string, append to rich presence
    }

    return Ok((discord_status, discord_rich_presence));
}
