// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
mod config;
use config::*;
mod domain_or_ip;
mod error;
mod main_inner;
use main_inner::*;
mod rich_presence;


fn main() -> std::process::ExitCode
{
    let mut crate_logging_level: std::collections::HashMap<String, log::Level> = std::collections::HashMap::new(); // logging level for individual crates
    let config: Config; // config, settings
    let tokio_rt: tokio::runtime::Runtime = tokio::runtime::Runtime::new().expect("Creating tokio runtime failed."); // async runtime


    std::panic::set_hook(Box::new(|panic_info: &std::panic::PanicInfo| // override panic behaviour
    {
        log::error!("{}", panic_info); // log panic source and reason
        log::error!("{}", std::backtrace::Backtrace::capture()); // log backtrace
    }));

    match load_config::load_config // load config
    (
        vec!
        [
            load_config::Source::Env,
            load_config::Source::File(load_config::SourceFile::Toml("./config/.env".to_string())),
        ],
        Some(load_config::SourceFile::Toml("./config/.env".to_string())),
    )
    {
        Ok(o) => config = o, // loaded config successfully
        Err(e) => // loading config failed
        {
            setup_logging::setup_logging(log::Level::Info, None, "./log/%Y-%m-%d.log"); // setup logging with default settings to log error
            log::error!("{e}");
            return std::process::ExitCode::FAILURE;
        }
    }

    crate_logging_level.insert("serenity".to_owned(), log::Level::Warn); // shut up
    crate_logging_level.insert("tracing::span".to_owned(), log::Level::Warn); // shut up
    if config.DEBUG.unwrap_or(false) // setup logging, if DEBUG unset default to false
    {
        setup_logging::setup_logging(log::Level::Debug, Some(crate_logging_level), "./log/%Y-%m-%dT%H_%M.log");
    }
    else
    {
        setup_logging::setup_logging(log::Level::Info, Some(crate_logging_level), "./log/%Y-%m-%d.log");
    }

    log::debug!("Loaded {config:?}."); // log loaded config


    match std::panic::catch_unwind(|| tokio_rt.block_on(main_inner(config))) // execute main_inner, catch panic
    {
        Ok(result) => // no panic
        {
            match result
            {
                Ok(()) => {return std::process::ExitCode::SUCCESS;} // program executed successfully
                Err(e) => // program failed in a controlled manner
                {
                    log::error!("{e}"); // log error
                    return std::process::ExitCode::FAILURE;
                }
            }
        }
        Err(_) => {return std::process::ExitCode::FAILURE;} // program crashed with panic, dis not good
    };
}