use std::path::PathBuf;

/// All errors that can occur in the Attio CLI.
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Configuration error: {0}")]
    Config(#[from] ConfigError),

    #[error("API error: {0}")]
    Api(#[from] ApiError),

    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),

    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("{0}")]
    Input(String),
}

/// Configuration-related errors.
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("No API key configured. Run `attio config set api-key <token>` or set ATTIO_API_KEY")]
    MissingApiKey,

    #[error("Failed to read config file at {path}: {source}")]
    ReadFile {
        path: PathBuf,
        source: std::io::Error,
    },

    #[error("Failed to write config file at {path}: {source}")]
    WriteFile {
        path: PathBuf,
        source: std::io::Error,
    },

    #[error("Failed to parse config file: {0}")]
    Parse(#[from] toml::de::Error),

    #[error("Failed to serialize config: {0}")]
    Serialize(#[from] toml::ser::Error),

    #[error("Could not determine config directory")]
    NoConfigDir,
}

/// Attio API errors.
#[derive(Debug, thiserror::Error)]
pub enum ApiError {
    #[error("Unauthorized: check your API key")]
    Unauthorized,

    #[error("Forbidden: missing required scope '{scope}'")]
    Forbidden { scope: String },

    #[error("Not found: {resource} '{id}' does not exist")]
    NotFound { resource: String, id: String },

    #[error("Validation error: {message}")]
    Validation { message: String },

    #[error("Rate limited: retry after {retry_after_secs} seconds")]
    RateLimited { retry_after_secs: u64 },

    #[error("Server error ({status}): {message}")]
    Server { status: u16, message: String },
}

pub type Result<T> = std::result::Result<T, Error>;
