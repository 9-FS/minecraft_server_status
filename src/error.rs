// Copyright (c) 2024 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.


#[derive(Debug, thiserror::Error)]
pub enum Error
{
    #[error("Setting {name} has invalid value \"{value}\", reason: {reason}")]
    SettingInvalid {name: String, value: String, reason: String},

    #[error("Starting discord bot failed with: {0}")]
    Serenity(#[from] serenity::Error),
}