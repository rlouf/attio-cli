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

    /// Manage lists (pipelines, workflows)
    Lists {
        #[command(subcommand)]
        command: ListsCommands,
    },

    /// Manage list entries
    Entries {
        #[command(subcommand)]
        command: EntriesCommands,
    },

    /// Manage tasks
    Tasks {
        #[command(subcommand)]
        command: TasksCommands,
    },

    /// Manage notes
    Notes {
        #[command(subcommand)]
        command: NotesCommands,
    },

    /// Manage object attributes
    Attributes {
        #[command(subcommand)]
        command: AttributesCommands,
    },

    /// Manage workspace members
    Members {
        #[command(subcommand)]
        command: MembersCommands,
    },

    /// Manage webhooks
    Webhooks {
        #[command(subcommand)]
        command: WebhooksCommands,
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
enum ListsCommands {
    /// List all lists
    List {
        /// Output as JSON/JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get list details
    Get {
        /// List slug or ID
        list: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum EntriesCommands {
    /// List entries in a list
    List {
        /// List slug or ID
        list: String,

        /// Maximum number of entries to return
        #[arg(long)]
        limit: Option<u32>,

        /// Number of entries to skip
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

    /// Get an entry by ID
    Get {
        /// List slug or ID
        list: String,

        /// Entry ID
        entry_id: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Add a record to a list
    Create {
        /// List slug or ID
        list: String,

        /// Record ID to add to the list
        #[arg(long)]
        record_id: String,

        /// JSON data for entry values (or pass via stdin)
        data: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Update an entry
    Update {
        /// List slug or ID
        list: String,

        /// Entry ID
        entry_id: String,

        /// JSON data (or pass via stdin)
        data: Option<String>,

        /// Overwrite multiselect values instead of appending
        #[arg(long)]
        overwrite: bool,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum TasksCommands {
    /// List tasks
    List {
        /// Maximum number of tasks to return
        #[arg(long)]
        limit: Option<u32>,

        /// Number of tasks to skip
        #[arg(long)]
        offset: Option<u32>,

        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get a task by ID
    Get {
        /// Task ID
        task_id: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Create a new task
    Create {
        /// Task content
        content: String,

        /// Deadline (ISO 8601 format)
        #[arg(long)]
        deadline: Option<String>,

        /// Assignees as JSON array
        #[arg(long)]
        assignees: Option<String>,

        /// Linked records as JSON array
        #[arg(long)]
        linked_records: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Update a task
    Update {
        /// Task ID
        task_id: String,

        /// New task content
        #[arg(long)]
        content: Option<String>,

        /// Mark as completed
        #[arg(long)]
        completed: Option<bool>,

        /// New deadline (ISO 8601 format)
        #[arg(long)]
        deadline: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum NotesCommands {
    /// List notes
    List {
        /// Filter by parent object type
        #[arg(long)]
        parent_object: Option<String>,

        /// Filter by parent record ID
        #[arg(long)]
        parent_record_id: Option<String>,

        /// Maximum number of notes to return
        #[arg(long)]
        limit: Option<u32>,

        /// Number of notes to skip
        #[arg(long)]
        offset: Option<u32>,

        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get a note by ID
    Get {
        /// Note ID
        note_id: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Create a new note
    Create {
        /// Note title
        #[arg(long)]
        title: String,

        /// Parent object type (people, companies, etc.)
        #[arg(long)]
        parent_object: String,

        /// Parent record ID
        #[arg(long)]
        parent_record_id: String,

        /// Note content
        #[arg(long)]
        content: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum AttributesCommands {
    /// List attributes for an object
    List {
        /// Object slug or ID
        object: String,

        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get attribute details
    Get {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Create a new attribute
    Create {
        /// Object slug or ID
        object: String,

        /// Attribute title
        #[arg(long)]
        title: String,

        /// Attribute type (text, number, select, status, etc.)
        #[arg(long, name = "type")]
        attr_type: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Update an attribute
    Update {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// New title
        #[arg(long)]
        title: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// List select options for an attribute
    Options {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Add a select option
    AddOption {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// Option title
        #[arg(long)]
        title: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Update a select option
    UpdateOption {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// Option ID
        option_id: String,

        /// New title
        #[arg(long)]
        title: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// List status options for an attribute
    Statuses {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Add a status option
    AddStatus {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// Status title
        #[arg(long)]
        title: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Update a status option
    UpdateStatus {
        /// Object slug or ID
        object: String,

        /// Attribute slug or ID
        attribute: String,

        /// Status ID
        status_id: String,

        /// New title
        #[arg(long)]
        title: Option<String>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum MembersCommands {
    /// List workspace members
    List {
        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get member details
    Get {
        /// Member ID
        member_id: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum WebhooksCommands {
    /// List webhooks
    List {
        /// Output as JSONL
        #[arg(long)]
        json: bool,
    },

    /// Get webhook details
    Get {
        /// Webhook ID
        webhook_id: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Create a new webhook
    Create {
        /// Target URL
        #[arg(long)]
        target_url: String,

        /// Comma-separated event types (e.g., "record.created,record.updated")
        #[arg(long)]
        subscriptions: String,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Update a webhook
    Update {
        /// Webhook ID
        webhook_id: String,

        /// New target URL
        #[arg(long)]
        target_url: Option<String>,

        /// New subscriptions (comma-separated)
        #[arg(long)]
        subscriptions: Option<String>,

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

        Commands::Lists { command } => {
            let client = create_client()?;
            match command {
                ListsCommands::List { json } => {
                    commands::lists::list(&client, json).await?;
                }
                ListsCommands::Get { list, json } => {
                    commands::lists::get(&client, &list, json).await?;
                }
            }
        }

        Commands::Entries { command } => {
            let client = create_client()?;
            match command {
                EntriesCommands::List {
                    list,
                    limit,
                    offset,
                    filter,
                    sort,
                    json,
                } => {
                    commands::entries::list(
                        &client,
                        &list,
                        limit,
                        offset,
                        filter.as_deref(),
                        sort.as_deref(),
                        json,
                    )
                    .await?;
                }
                EntriesCommands::Get {
                    list,
                    entry_id,
                    json,
                } => {
                    commands::entries::get(&client, &list, &entry_id, json).await?;
                }
                EntriesCommands::Create {
                    list,
                    record_id,
                    data,
                    json,
                } => {
                    commands::entries::create(&client, &list, &record_id, data.as_deref(), json)
                        .await?;
                }
                EntriesCommands::Update {
                    list,
                    entry_id,
                    data,
                    overwrite,
                    json,
                } => {
                    commands::entries::update(
                        &client,
                        &list,
                        &entry_id,
                        data.as_deref(),
                        overwrite,
                        json,
                    )
                    .await?;
                }
            }
        }

        Commands::Tasks { command } => {
            let client = create_client()?;
            match command {
                TasksCommands::List { limit, offset, json } => {
                    commands::tasks::list(&client, limit, offset, json).await?;
                }
                TasksCommands::Get { task_id, json } => {
                    commands::tasks::get(&client, &task_id, json).await?;
                }
                TasksCommands::Create {
                    content,
                    deadline,
                    assignees,
                    linked_records,
                    json,
                } => {
                    commands::tasks::create(
                        &client,
                        &content,
                        deadline.as_deref(),
                        assignees.as_deref(),
                        linked_records.as_deref(),
                        json,
                    )
                    .await?;
                }
                TasksCommands::Update {
                    task_id,
                    content,
                    completed,
                    deadline,
                    json,
                } => {
                    commands::tasks::update(
                        &client,
                        &task_id,
                        content.as_deref(),
                        completed,
                        deadline.as_deref(),
                        json,
                    )
                    .await?;
                }
            }
        }

        Commands::Notes { command } => {
            let client = create_client()?;
            match command {
                NotesCommands::List {
                    parent_object,
                    parent_record_id,
                    limit,
                    offset,
                    json,
                } => {
                    commands::notes::list(
                        &client,
                        parent_object.as_deref(),
                        parent_record_id.as_deref(),
                        limit,
                        offset,
                        json,
                    )
                    .await?;
                }
                NotesCommands::Get { note_id, json } => {
                    commands::notes::get(&client, &note_id, json).await?;
                }
                NotesCommands::Create {
                    title,
                    parent_object,
                    parent_record_id,
                    content,
                    json,
                } => {
                    commands::notes::create(
                        &client,
                        &title,
                        &parent_object,
                        &parent_record_id,
                        content.as_deref(),
                        json,
                    )
                    .await?;
                }
            }
        }

        Commands::Attributes { command } => {
            let client = create_client()?;
            match command {
                AttributesCommands::List { object, json } => {
                    commands::attributes::list(&client, &object, json).await?;
                }
                AttributesCommands::Get {
                    object,
                    attribute,
                    json,
                } => {
                    commands::attributes::get(&client, &object, &attribute, json).await?;
                }
                AttributesCommands::Create {
                    object,
                    title,
                    attr_type,
                    json,
                } => {
                    commands::attributes::create(&client, &object, &title, &attr_type, json)
                        .await?;
                }
                AttributesCommands::Update {
                    object,
                    attribute,
                    title,
                    json,
                } => {
                    commands::attributes::update(&client, &object, &attribute, title.as_deref(), json)
                        .await?;
                }
                AttributesCommands::Options {
                    object,
                    attribute,
                    json,
                } => {
                    commands::attributes::list_options(&client, &object, &attribute, json).await?;
                }
                AttributesCommands::AddOption {
                    object,
                    attribute,
                    title,
                    json,
                } => {
                    commands::attributes::create_option(&client, &object, &attribute, &title, json)
                        .await?;
                }
                AttributesCommands::UpdateOption {
                    object,
                    attribute,
                    option_id,
                    title,
                    json,
                } => {
                    commands::attributes::update_option(
                        &client,
                        &object,
                        &attribute,
                        &option_id,
                        title.as_deref(),
                        json,
                    )
                    .await?;
                }
                AttributesCommands::Statuses {
                    object,
                    attribute,
                    json,
                } => {
                    commands::attributes::list_statuses(&client, &object, &attribute, json).await?;
                }
                AttributesCommands::AddStatus {
                    object,
                    attribute,
                    title,
                    json,
                } => {
                    commands::attributes::create_status(&client, &object, &attribute, &title, json)
                        .await?;
                }
                AttributesCommands::UpdateStatus {
                    object,
                    attribute,
                    status_id,
                    title,
                    json,
                } => {
                    commands::attributes::update_status(
                        &client,
                        &object,
                        &attribute,
                        &status_id,
                        title.as_deref(),
                        json,
                    )
                    .await?;
                }
            }
        }

        Commands::Members { command } => {
            let client = create_client()?;
            match command {
                MembersCommands::List { json } => {
                    commands::members::list(&client, json).await?;
                }
                MembersCommands::Get { member_id, json } => {
                    commands::members::get(&client, &member_id, json).await?;
                }
            }
        }

        Commands::Webhooks { command } => {
            let client = create_client()?;
            match command {
                WebhooksCommands::List { json } => {
                    commands::webhooks::list(&client, json).await?;
                }
                WebhooksCommands::Get { webhook_id, json } => {
                    commands::webhooks::get(&client, &webhook_id, json).await?;
                }
                WebhooksCommands::Create {
                    target_url,
                    subscriptions,
                    json,
                } => {
                    commands::webhooks::create(&client, &target_url, &subscriptions, json).await?;
                }
                WebhooksCommands::Update {
                    webhook_id,
                    target_url,
                    subscriptions,
                    json,
                } => {
                    commands::webhooks::update(
                        &client,
                        &webhook_id,
                        target_url.as_deref(),
                        subscriptions.as_deref(),
                        json,
                    )
                    .await?;
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
