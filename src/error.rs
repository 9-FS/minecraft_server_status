// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.


#[derive(Debug, thiserror::Error)]
pub enum Error
{
    #[error("Setting {name} has invalid value \"{value}\", reason: {reason}")]
    SettingInvalid {name: String, value: String, reason: String},

    #[error(transparent)]
    Serenity(#[from] serenity::Error),
}


pub type Result<T> = std::result::Result<T, Error>; // strict error handling, only takes pre defined Error type