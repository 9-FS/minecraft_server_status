// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
use crate::domain_or_ip::*;
use std::io::Write;


/// # Summary
/// Collection of settings making up the configuration of the application.
#[derive(Debug, serde::Deserialize, serde::Serialize)]
#[allow(non_snake_case)]
pub struct Config
{
    pub DISCORD_BOT_TOKEN:             String,      // discord bot token
    pub MINECRAFT_SERVER_DOMAIN_OR_IP: DomainOrIp,  // minecraft server domain or ip, do not add port here
    pub MINECRAFT_SERVER_PORT:         Option<u16>, // minecraft server port, optional
    pub REFRESH_INTERVAL:              u64,         // refresh display every `REFRESH_INTERVAL` seconds
}

impl Default for Config
{
    fn default() -> Self
    {
        Config {
            DISCORD_BOT_TOKEN:             "".to_owned(),
            MINECRAFT_SERVER_DOMAIN_OR_IP: DomainOrIp::Domain("".to_owned()),
            MINECRAFT_SERVER_PORT:         Some(25565),
            REFRESH_INTERVAL:              5,
        }
    }
}


impl Config
{
    /// # Summary
    /// Offers to create a default configuration file at `filepath` if it does not exist. The file will be created in the format specified by `file_format`.
    ///
    /// # Arguments
    /// - `filepath`: Path to the file to be created.
    /// - `file_format`: Format of the file to be created.
    pub fn offer_default_file_creation(filepath: &str, file_format: FileFormat) -> ()
    {
        let mut file: std::fs::File; // file to write to
        let file_content: String; // Config serialised to write to file


        if std::path::Path::new(filepath).exists()
        // if file already exists
        {
            return; // don't want to overwrite anything
        }

        loop
        {
            log::info!("Would you like to create a default config file at \"{filepath}\"? (y/n)");
            let mut input: String = String::new();
            _ = std::io::stdin().read_line(&mut input); // read input
            match input.trim()
            {
                "y" =>
                // offer accepted, create default config file
                {
                    break;
                }
                "n" =>
                // offer denied, don't do anything
                {
                    return;
                }
                _ =>
                // input invalid, ask again
                {
                    log::error!("Invalid input.");
                    continue;
                }
            }
        }


        match file_format
        {
            #[cfg(feature = "load_json_config")]
            FileFormat::Json =>
            {
                match serde_json::to_string_pretty(&Config::default()) // serialise config to json
                {
                    Ok(s) =>
                    {
                        file_content = s;
                    }
                    Err(e) =>
                    {
                        log::error!("Serialising \"{:?}\" to json failed with: {}", &Config::default(), e);
                        return;
                    }
                };
            }
            #[cfg(feature = "load_toml_config")]
            FileFormat::Toml =>
            {
                match toml::to_string_pretty(&Config::default()) // serialise config to toml
                {
                    Ok(s) =>
                    {
                        file_content = s;
                    }
                    Err(e) =>
                    {
                        log::error!("Serialising \"{:?}\" to toml failed with: {}", &Config::default(), e);
                        return;
                    }
                };
            }
            #[cfg(feature = "load_yaml_config")]
            FileFormat::Yaml =>
            {
                match serde_yaml::to_string(&Config::default()) // serialise config to yaml
                {
                    Ok(s) =>
                    {
                        file_content = s;
                    }
                    Err(e) =>
                    {
                        log::error!("Serialising \"{:?}\" to yaml failed with: {}", &Config::default(), e);
                        return;
                    }
                };
            }
        };

        match std::fs::File::create_new(filepath) // create new file, fails if already exists, don't want to overwrite anything
        {
            Ok(f) =>
            {
                file = f;
            }
            Err(e) =>
            {
                log::error!("Creating default config file at \"{filepath}\" failed with: {e}");
                return;
            }
        };

        match file.write_all(file_content.as_bytes()) // write string to file
        {
            Ok(_) =>
            {
                log::info!("Created default config file at \"{filepath}\".");
            }
            Err(e) =>
            {
                log::error!("Writing config to \"{filepath}\" failed with: {e}");
                return;
            }
        };

        return;
    }
}


/// # Summary
/// Enum representing the supported formats of a config file. Conditional compilation is used to only activate the variants that are supported by the features enabled.
pub enum FileFormat
{
    #[cfg(feature = "load_json_config")]
    Json,
    #[cfg(feature = "load_toml_config")]
    Toml,
    #[cfg(feature = "load_yaml_config")]
    Yaml,
}
