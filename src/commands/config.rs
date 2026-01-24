use crate::config::Config;
use crate::error::Result;

/// Show current configuration.
pub fn show() -> Result<()> {
    let config = Config::load()?;
    let path = Config::path()?;

    println!("Config file: {}", path.display());
    println!();

    if let Some(ref key) = config.api_key {
        // Mask the API key
        let masked = if key.len() > 8 {
            format!("{}...{}", &key[..4], &key[key.len() - 4..])
        } else {
            "*".repeat(key.len())
        };
        println!("api_key: {}", masked);
    } else {
        println!("api_key: (not set)");
    }

    // Check for environment variable
    if std::env::var("ATTIO_API_KEY").is_ok() {
        println!();
        println!("Note: ATTIO_API_KEY environment variable is set (takes precedence)");
    }

    Ok(())
}

/// Set a configuration value.
pub fn set(key: &str, value: &str) -> Result<()> {
    let mut config = Config::load()?;

    match key {
        "api-key" => {
            config.api_key = Some(value.to_string());
            config.save()?;
            println!("API key saved.");
        }
        _ => {
            eprintln!("Unknown config key: {}", key);
            eprintln!("Available keys: api-key");
            std::process::exit(1);
        }
    }

    Ok(())
}
