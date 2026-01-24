# Attio CLI Implementation Plan

A Rust command-line interface for interacting with Attio's CRM API.

## Overview

**Attio** is an AI-native CRM platform designed for Go-to-Market teams. It supports flexible data modeling with:
- Standard objects: **people**, **companies**, **deals**, **users**
- Unlimited custom objects
- Lists for organizing records with custom workflows
- Tasks, Notes, and collaboration features

**API Base URL**: `https://api.attio.com/v2/`

## Authentication

The CLI will support:

1. **Bearer Token** (Primary): API access token from Attio workspace settings
   - Token passed via `Authorization: Bearer <token>` header
   - Scopes control access (e.g., `record_permission:read`, `object_configuration:read`)

2. **Environment Variable**: `ATTIO_API_KEY`

3. **Config File**: `~/.config/attio/config.toml` for persistent configuration

---

## Implementation Phases (Ordered by Priority)

### Phase 1: Foundation & Records (Highest Priority)

#### 1.1 Project Setup
```
attio-cli/
├── Cargo.toml
├── src/
│   ├── main.rs           # Entry point, CLI parsing
│   ├── lib.rs            # Library exports
│   ├── client.rs         # HTTP client wrapper
│   ├── config.rs         # Configuration management
│   ├── error.rs          # Error types
│   ├── output.rs         # Output formatting (JSON, table, etc.)
│   └── commands/
│       ├── mod.rs
│       ├── config.rs     # Configuration commands
│       ├── records.rs    # Record operations (people, companies, etc.)
│       ├── lists.rs      # List management
│       ├── entries.rs    # List entry operations
│       ├── tasks.rs      # Task management
│       ├── notes.rs      # Note operations
│       ├── objects.rs    # Object schema operations
│       ├── attributes.rs # Attribute management
│       ├── webhooks.rs   # Webhook management
│       ├── members.rs    # Workspace members
│       ├── threads.rs    # Threads & comments
│       └── meetings.rs   # Meetings & recordings
```

#### 1.2 Configuration Commands
```bash
# Initialize configuration interactively
attio config init

# Set configuration values
attio config set api-key <token>
attio config set output [json|table|yaml]

# View current configuration
attio config show
```

#### 1.3 Identity Check
```bash
# Verify authentication and show workspace info (GET /v2/self)
attio whoami
```

#### 1.4 Records Commands (Core CRUD)
Unified interface for all object types: `people`, `companies`, `deals`, `users`, or any custom object.

```bash
# List records with optional filters and sorting
attio records list <object> [--limit N] [--offset N] [--filter <json>] [--sort <json>]

# Get a specific record by ID
attio records get <object> <record_id>

# Create a new record
attio records create <object> --data '<json>'
# Examples:
#   attio records create people --data '{"name": "John Doe", "email_addresses": ["john@example.com"]}'
#   attio records create companies --data '{"name": "Acme Corp", "domains": ["acme.com"]}'

# Assert a record (upsert - create or update if matching)
attio records assert <object> --match-attr <attribute> --data '<json>'
# Example:
#   attio records assert people --match-attr email_addresses --data '{"email_addresses": ["john@example.com"], "name": "John Doe"}'

# Update a record (append to multiselect values)
attio records update <object> <record_id> --data '<json>'

# Update a record (overwrite multiselect values)
attio records update <object> <record_id> --data '<json>' --overwrite

# Delete a record
attio records delete <object> <record_id>

# Get attribute values for a record
attio records attributes <object> <record_id> [--attribute <attr>] [--show-historic]

# List entries (lists this record belongs to)
attio records entries <object> <record_id>

# Search records (fuzzy match on names, emails, domains, phones)
attio records search <object> <query> [--limit N]
```

---

### Phase 2: Lists & Entries (Workflow Management)

#### 2.1 Lists Commands
Lists organize records into workflows (e.g., Sales Pipeline, Hiring Pipeline).

```bash
# List all lists in workspace
attio lists list

# Get list details
attio lists get <list>

# Create a new list
attio lists create --name "Sales Pipeline" --parent-object companies

# Update a list
attio lists update <list> --name "Enterprise Pipeline"
```

#### 2.2 Entries Commands
Entries represent records within a list (e.g., a company in your Sales Pipeline).

```bash
# List/query entries in a list
attio entries list <list> [--filter <json>] [--sort <json>] [--limit N]

# Get entry details
attio entries get <list> <entry_id>

# Add a record to a list (create entry)
attio entries create <list> --record-id <record_id> [--data '<json>']

# Assert an entry (create if not exists)
attio entries assert <list> --parent-record <record_id> [--data '<json>']

# Update entry (append to multiselect values)
attio entries update <list> <entry_id> --data '<json>'

# Update entry (overwrite multiselect values)
attio entries update <list> <entry_id> --data '<json>' --overwrite

# Remove entry from list
attio entries delete <list> <entry_id>

# Get entry attribute values
attio entries attributes <list> <entry_id>
```

---

### Phase 3: Tasks & Notes (Productivity)

#### 3.1 Tasks Commands
```bash
# List all tasks
attio tasks list [--limit N] [--assignee <member_id>]

# Get a task
attio tasks get <task_id>

# Create a task
attio tasks create --content "Follow up with client" \
    [--deadline "2025-01-30"] \
    [--assignee <member_id>] \
    [--linked-records '<json>']

# Update a task
attio tasks update <task_id> [--content "..."] [--completed true] [--deadline "..."]

# Delete a task
attio tasks delete <task_id>
```

#### 3.2 Notes Commands
```bash
# List notes
attio notes list [--parent-object <object>] [--parent-record <record_id>] [--limit N]

# Get a note
attio notes get <note_id>

# Create a note
attio notes create --title "Meeting Notes" \
    --parent-object people \
    --parent-record <record_id> \
    [--content "Discussed Q1 goals..."]

# Delete a note
attio notes delete <note_id>
```

---

### Phase 4: Schema Management (Objects & Attributes)

#### 4.1 Objects Commands
```bash
# List all objects (standard + custom)
attio objects list

# Get object schema details
attio objects get <object>

# Create a custom object
attio objects create --api-slug "deals" --singular-noun "Deal" --plural-noun "Deals"

# Update an object
attio objects update <object> [--singular-noun "..."] [--plural-noun "..."]
```

#### 4.2 Attributes Commands
```bash
# List attributes for an object
attio attributes list <object>

# Get attribute details
attio attributes get <object> <attribute>

# Create an attribute
attio attributes create <object> --title "Priority" --type select

# Update an attribute
attio attributes update <object> <attribute> --title "Urgency"

# --- Select Options ---
# List select options
attio attributes options <object> <attribute>

# Add a select option
attio attributes add-option <object> <attribute> --title "High" [--color "red"]

# Update a select option
attio attributes update-option <object> <attribute> <option_id> --title "Critical"

# --- Status Options ---
# List statuses
attio attributes statuses <object> <attribute>

# Add a status
attio attributes add-status <object> <attribute> --title "In Progress"

# Update a status
attio attributes update-status <object> <attribute> <status_id> --title "Active"
```

---

### Phase 5: Webhooks

```bash
# List webhooks
attio webhooks list

# Get webhook details
attio webhooks get <webhook_id>

# Create webhook
attio webhooks create --target-url "https://example.com/webhook" \
    --subscriptions "record.created,record.updated,task.created"

# Update webhook
attio webhooks update <webhook_id> [--target-url "..."] [--subscriptions "..."]

# Delete webhook
attio webhooks delete <webhook_id>
```

**Available Webhook Events:**
- `record.created`, `record.updated`, `record.deleted`
- `list_entry.created`, `list_entry.updated`, `list_entry.deleted`
- `note.created`, `note.updated`, `note.deleted`
- `task.created`, `task.updated`, `task.deleted`
- `comment.created`, `comment.deleted`
- `object_attribute.created`, `object_attribute.updated`
- `list_attribute.created`, `list_attribute.updated`
- `workspace_member.added`, `workspace_member.removed`

---

### Phase 6: Workspace & Collaboration

#### 6.1 Members Commands
```bash
# List workspace members
attio members list

# Get member details
attio members get <member_id>
```

#### 6.2 Threads & Comments
```bash
# List threads
attio threads list [--record-id <id>]

# Get thread
attio threads get <thread_id>

# Create comment on a thread
attio comments create <thread_id> --content "Great progress!"

# Get comment
attio comments get <comment_id>

# Delete comment
attio comments delete <comment_id>
```

---

### Phase 7: Meetings & Recordings (Beta)

```bash
# List meetings
attio meetings list [--limit N]

# Get meeting details
attio meetings get <meeting_id>

# List call recordings for a meeting
attio recordings list <meeting_id>

# Get call recording
attio recordings get <recording_id>

# Get transcript for a recording
attio transcripts get <recording_id>
```

---

## Technical Implementation Details

### Dependencies (Cargo.toml)
```toml
[package]
name = "attio"
version = "0.1.0"
edition = "2021"
description = "CLI for interacting with Attio CRM API"

[dependencies]
# CLI framework
clap = { version = "4", features = ["derive", "env"] }

# Async runtime
tokio = { version = "1", features = ["full"] }

# HTTP client
reqwest = { version = "0.12", features = ["json", "rustls-tls"] }

# JSON handling
serde = { version = "1", features = ["derive"] }
serde_json = "1"

# Error handling
thiserror = "2"
anyhow = "1"

# Configuration
toml = "0.8"
dirs = "6"

# Output formatting
tabled = "0.17"
colored = "2"
chrono = { version = "0.4", features = ["serde"] }
```

### API Scopes Required

| Feature | Required Scopes |
|---------|-----------------|
| Read records | `record_permission:read`, `object_configuration:read` |
| Write records | `record_permission:read_write`, `object_configuration:read` |
| Read lists/entries | `list_entry:read`, `list_configuration:read` |
| Write entries | `list_entry:read_write`, `list_configuration:read` |
| Tasks | `task:read` or `task:read_write`, `object_configuration:read`, `record_permission:read`, `user_management:read` |
| Notes | `note:read` or `note:read_write`, `record_permission:read` |
| Webhooks | `webhook:read` or `webhook:read_write` |
| Workspace members | `user_management:read` |
| Meetings/Recordings | `meeting:read`, `call_recording:read` |

### Error Handling

The CLI should handle:
- Authentication errors (401) → prompt to check API key
- Permission errors (403) → indicate missing scopes
- Not found errors (404) → clear "resource not found" message
- Validation errors (400/422) → display API error details
- Rate limiting (429) → implement exponential backoff
- Network errors → retry with backoff

### Output Formats

Support multiple output formats via `--output` or `-o` flag:
- `table` (default): Human-readable table format
- `json`: Compact JSON for scripting
- `json-pretty`: Formatted JSON
- `yaml`: YAML format
- `ids`: Just IDs, one per line (for piping)

---

## Command Priority Summary

### Tier 1 (Must Have - Daily Operations)
1. `attio config *` - Setup and configuration
2. `attio whoami` - Verify authentication
3. `attio records *` - CRUD for people, companies, deals, custom objects

### Tier 2 (Should Have - Workflow Management)
4. `attio lists *` - List management
5. `attio entries *` - Entry operations
6. `attio tasks *` - Task management
7. `attio notes *` - Note operations

### Tier 3 (Nice to Have - Administration)
8. `attio objects *` - Schema management
9. `attio attributes *` - Attribute configuration
10. `attio webhooks *` - Integration hooks
11. `attio members *` - Team info

### Tier 4 (Advanced - Specialized Use)
12. `attio threads/comments` - Collaboration
13. `attio meetings/recordings` - Call intelligence

---

## Next Steps

1. **Initialize Rust project** with Cargo
2. **Implement HTTP client** with authentication
3. **Build config management** system
4. **Implement records commands** (list, get, create, update, delete, search)
5. **Add lists and entries commands**
6. **Build out remaining commands** in priority order
7. **Add comprehensive error handling**
8. **Write tests** for each command
9. **Create shell completions** (bash, zsh, fish)
10. **Package for distribution**

---

## Sources

- [Attio REST API Overview](https://docs.attio.com/rest-api/overview)
- [Attio Authentication Guide](https://docs.attio.com/rest-api/how-to/authentication)
- [Attio Filtering and Sorting](https://docs.attio.com/rest-api/how-to/filtering-and-sorting)
- [Attio OpenAPI Spec](https://docs.attio.com/rest-api/endpoint-reference/openapi)
- [Attio JS SDK (Community)](https://github.com/d-stoll/attio-js)
