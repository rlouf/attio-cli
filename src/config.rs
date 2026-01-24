use crate::error::{ConfigError, Result};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

const CONFIG_DIR: &str = "attio";
const CONFIG_FILE: &str = "config.toml";
const ENV_API_KEY: &str = "ATTIO_API_KEY";
const ENV_ALLOW_DESTRUCTIVE: &str = "ATTIO_ALLOW_DESTRUCTIVE";

/// Check if destructive operations are allowed.
pub fn allow_destructive() -> bool {
    std::env::var(ENV_ALLOW_DESTRUCTIVE)
        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
        .unwrap_or(false)
}

/// Require destructive operations to be enabled, or return an error.
pub fn require_destructive() -> Result<()> {
    if allow_destructive() {
        Ok(())
    } else {
        Err(ConfigError::DestructiveDisabled.into())
    }
}

/// Persistent configuration stored in config file.
#[derive(Debug, Default, Serialize, Deserialize)]
pub struct Config {
    pub api_key: Option<String>,
}

impl Config {
    /// Load config from file, or return default if file doesn't exist.
    pub fn load() -> Result<Self> {
        let path = Self::path()?;

        if !path.exists() {
            return Ok(Self::default());
        }

        let contents = std::fs::read_to_string(&path).map_err(|source| {
            ConfigError::ReadFile {
                path: path.clone(),
                source,
            }
        })?;

        let config: Config = toml::from_str(&contents).map_err(ConfigError::Parse)?;
        Ok(config)
    }

    /// Save config to file.
    pub fn save(&self) -> Result<()> {
        let path = Self::path()?;

        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).map_err(|source| ConfigError::WriteFile {
                path: parent.to_path_buf(),
                source,
            })?;
        }

        let contents = toml::to_string_pretty(self).map_err(ConfigError::Serialize)?;
        std::fs::write(&path, contents).map_err(|source| ConfigError::WriteFile { path, source })?;

        Ok(())
    }

    /// Get the config file path.
    pub fn path() -> Result<PathBuf> {
        let config_dir = dirs::config_dir().ok_or(ConfigError::NoConfigDir)?;
        Ok(config_dir.join(CONFIG_DIR).join(CONFIG_FILE))
    }

    /// Get API key from environment or config file.
    /// Environment variable takes precedence.
    pub fn api_key(&self) -> Result<String> {
        // Environment variable takes precedence
        if let Ok(key) = std::env::var(ENV_API_KEY) {
            if !key.is_empty() {
                return Ok(key);
            }
        }

        // Fall back to config file
        self.api_key
            .clone()
            .filter(|k| !k.is_empty())
            .ok_or_else(|| ConfigError::MissingApiKey.into())
    }
}
