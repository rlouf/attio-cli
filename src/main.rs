use attio::client::AttioClient;
use attio::commands;
use attio::config::Config;
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "attio")]
#[command(about = "CLI for interacting with Attio CRM API")]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Show current workspace and authentication info
    Whoami {
        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Manage configuration
    Config {
        #[command(subcommand)]
        command: ConfigCommands,
    },

    /// Manage objects (schema)
    Objects {
        #[command(subcommand)]
        command: ObjectsCommands,
    },

    /// Manage records (people, companies, etc.)
    Records {
        #[command(subcommand)]
        command: RecordsCommands,
    },
}

#[derive(Subcommand)]
enum ConfigCommands {
    /// Show current configuration
    Show,

    /// Set a configuration value
    Set {
        /// Configuration key (api-key)
        key: String,
        /// Value to set
        value: String,
    },
}

#[derive(Subcommand)]
enum ObjectsCommands {
    /// List all objects
    List {
        /// Output as JSON/JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get object details
    Get {
        /// Object slug or ID
        object: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum RecordsCommands {
    /// List records
    List {
        /// Object type (people, companies, etc.)
        object: String,

        /// Maximum number of records to return
        #[arg(long)]
        limit: Option<u32>,

        /// Number of records to skip
        #[arg(long)]
        offset: Option<u32>,

        /// Filter as JSON
        #[arg(long)]
        filter: Option<String>,

        /// Sort as JSON
        #[arg(long)]
        sort: Option<String>,

        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get a record by ID
    Get {
        /// Object type
        object: String,

        /// Record ID
        record_id: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Create a new record
    Create {
        /// Object type
        object: String,

        /// JSON data (or pass via stdin)
        data: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Update a record
    Update {
        /// Object type
        object: String,

        /// Record ID
        record_id: String,

        /// JSON data (or pass via stdin)
        data: Option<String>,

        /// Overwrite multiselect values instead of appending
        #[arg(long)]
        overwrite: bool,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Delete a record
    Delete {
        /// Object type
        object: String,

        /// Record ID
        record_id: String,

        /// Skip confirmation prompt
        #[arg(long)]
        noconfirm: bool,
    },

    /// Search records
    Search {
        /// Object type
        object: String,

        /// Search query
        query: String,

        /// Maximum number of results
        #[arg(long)]
        limit: Option<u32>,

        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },
}

#[tokio::main]
async fn main() {
    if let Err(e) = run().await {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
}

async fn run() -> attio::error::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Config { command } => match command {
            ConfigCommands::Show => commands::config::show()?,
            ConfigCommands::Set { key, value } => commands::config::set(&key, &value)?,
        },

        // Commands that require authentication
        Commands::Whoami { json } => {
            let client = create_client()?;
            commands::whoami::execute(&client, json).await?;
        }

        Commands::Objects { command } => {
            let client = create_client()?;
            match command {
                ObjectsCommands::List { json } => {
                    commands::objects::list(&client, json).await?;
                }
                ObjectsCommands::Get { object, json } => {
                    commands::objects::get(&client, &object, json).await?;
                }
            }
        }

        Commands::Records { command } => {
            let client = create_client()?;
            match command {
                RecordsCommands::List {
                    object,
                    limit,
                    offset,
                    filter,
                    sort,
                    json,
                } => {
                    commands::records::list(
                        &client,
                        &object,
                        limit,
                        offset,
                        filter.as_deref(),
                        sort.as_deref(),
                        json,
                    )
                    .await?;
                }
                RecordsCommands::Get {
                    object,
                    record_id,
                    json,
                } => {
                    commands::records::get(&client, &object, &record_id, json).await?;
                }
                RecordsCommands::Create { object, data, json } => {
                    commands::records::create(&client, &object, data.as_deref(), json).await?;
                }
                RecordsCommands::Update {
                    object,
                    record_id,
                    data,
                    overwrite,
                    json,
                } => {
                    commands::records::update(
                        &client,
                        &object,
                        &record_id,
                        data.as_deref(),
                        overwrite,
                        json,
                    )
                    .await?;
                }
                RecordsCommands::Delete {
                    object,
                    record_id,
                    noconfirm,
                } => {
                    commands::records::delete(&client, &object, &record_id, noconfirm).await?;
                }
                RecordsCommands::Search {
                    object,
                    query,
                    limit,
                    json,
                } => {
                    commands::records::search(&client, &object, &query, limit, json).await?;
                }
            }
        }
    }

    Ok(())
}

fn create_client() -> attio::error::Result<AttioClient> {
    let config = Config::load()?;
    let api_key = config.api_key()?;
    AttioClient::new(api_key)
}
