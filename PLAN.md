# Attio CLI Implementation Plan

A Rust command-line interface for interacting with Attio's CRM API.

## Overview

**Attio** is an AI-native CRM platform designed for Go-to-Market teams. It supports flexible data modeling with:
- Standard CRM objects: **People**, **Companies**, **Deals**, **Users**
- Unlimited custom objects
- Lists for organizing records with custom workflows
- Tasks, Notes, and collaboration features

**API Base URL**: `https://api.attio.com/v2/`

## Authentication

The CLI will support two authentication methods:

1. **Bearer Token** (Primary): API access token from Attio workspace settings
   - Token passed via `Authorization: Bearer <token>` header
   - Scopes control access (e.g., `record_permission:read`, `object_configuration:read`)

2. **Environment Variable**: `ATTIO_API_KEY`

3. **Config File**: `~/.attio/config.toml` for persistent configuration

---

## Implementation Phases (Ordered by Priority)

### Phase 1: Foundation & Core Records (Highest Priority)

These are the most commonly used operations in any CRM workflow.

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
│       ├── auth.rs       # Authentication commands
│       ├── records.rs    # Record operations
│       ├── people.rs     # People-specific shortcuts
│       ├── companies.rs  # Company-specific shortcuts
│       ├── lists.rs      # List management
│       ├── entries.rs    # List entry operations
│       ├── tasks.rs      # Task management
│       ├── notes.rs      # Note operations
│       ├── objects.rs    # Object schema operations
│       ├── attributes.rs # Attribute management
│       ├── search.rs     # Search functionality
│       ├── webhooks.rs   # Webhook management
│       └── meta.rs       # Workspace info
```

#### 1.2 Authentication & Configuration Commands
```bash
# Initialize configuration
attio config init
attio config set api-key <token>
attio config set output-format [json|table|yaml]

# Verify authentication
attio auth whoami          # Uses GET /v2/self (Identify endpoint)
attio auth test            # Test API connectivity
```

#### 1.3 People Commands (High Priority)
People are the core of any CRM - contacts you interact with.

```bash
# List people with optional filters
attio people list [--limit N] [--offset N] [--filter <json>]

# Get a specific person
attio people get <record_id>

# Create a new person
attio people create --email "john@example.com" --name "John Doe" [--phone "+1234567890"]

# Assert (create or match) a person
attio people assert --email "john@example.com" --name "John Doe"

# Update a person
attio people update <record_id> --name "John Smith"

# Delete a person
attio people delete <record_id>

# Get attribute values for a person
attio people attributes <record_id>

# List entries (lists this person belongs to)
attio people entries <record_id>

# Search for people
attio people search "john"
```

#### 1.4 Companies Commands (High Priority)
Companies are the second most important object - the organizations you work with.

```bash
# List companies
attio companies list [--limit N] [--filter <json>]

# Get a specific company
attio companies get <record_id>

# Create a new company
attio companies create --name "Acme Corp" --domain "acme.com"

# Assert a company
attio companies assert --domain "acme.com" --name "Acme Corp"

# Update a company
attio companies update <record_id> --name "Acme Corporation"

# Delete a company
attio companies delete <record_id>

# Get attribute values
attio companies attributes <record_id>

# List entries
attio companies entries <record_id>
```

---

### Phase 2: Records & Lists (Core CRM Functionality)

#### 2.1 Generic Records Commands
For working with any object type (including custom objects).

```bash
# List records of any object type
attio records list <object> [--limit N] [--filter <json>] [--sort <json>]

# Query records with complex filters
attio records query <object> --filter '{"name": {"contains": "Acme"}}'

# Get a record
attio records get <object> <record_id>

# Create a record
attio records create <object> --data '{"name": "..."}'

# Assert a record (upsert)
attio records assert <object> --match-attr email --data '{"email_addresses": [...]}'

# Update a record (append multiselect values)
attio records update <object> <record_id> --data '{"tags": ["new-tag"]}'

# Update a record (overwrite multiselect values)
attio records overwrite <object> <record_id> --data '{"tags": ["only-tag"]}'

# Delete a record
attio records delete <object> <record_id>

# Search across records
attio records search <object> "query" [--limit N]
```

#### 2.2 Lists Commands
Lists organize records into workflows (e.g., Sales Pipeline, Hiring Pipeline).

```bash
# List all lists in workspace
attio lists list

# Get list details
attio lists get <list_id_or_slug>

# Create a new list
attio lists create --name "Sales Pipeline" --parent-object companies

# Update a list
attio lists update <list_id> --name "Enterprise Pipeline"
```

#### 2.3 Entries Commands
Entries are records within a list (e.g., a company in your Sales Pipeline).

```bash
# List entries in a list
attio entries list <list> [--filter <json>] [--limit N]

# Query entries with filters
attio entries query <list> --filter '{"status": "active"}'

# Add a record to a list (create entry)
attio entries create <list> --record-id <record_id> [--data '{"stage": "..."}']

# Assert an entry (create if not exists)
attio entries assert <list> --parent-record <record_id>

# Get entry details
attio entries get <list> <entry_id>

# Update entry (append)
attio entries update <list> <entry_id> --data '{"...": "..."}'

# Update entry (overwrite)
attio entries overwrite <list> <entry_id> --data '{"...": "..."}'

# Remove entry from list
attio entries delete <list> <entry_id>

# Get entry attribute values
attio entries attributes <list> <entry_id>
```

---

### Phase 3: Tasks & Notes (Productivity Features)

#### 3.1 Tasks Commands
Task management for CRM workflows.

```bash
# List all tasks
attio tasks list [--limit N] [--assignee <user_id>]

# Get a task
attio tasks get <task_id>

# Create a task
attio tasks create --content "Follow up with client" \
    [--deadline "2025-01-30"] \
    [--assignee <user_id>] \
    [--linked-records '["record_id1", "record_id2"]']

# Update a task
attio tasks update <task_id> --content "Updated content" [--completed true]

# Complete a task
attio tasks complete <task_id>

# Delete a task
attio tasks delete <task_id>
```

#### 3.2 Notes Commands
Notes attached to records.

```bash
# List notes
attio notes list [--parent-object <object>] [--parent-record <record_id>]

# Get a note
attio notes get <note_id>

# Create a note
attio notes create --title "Meeting Notes" \
    --content "Discussed Q1 goals..." \
    --parent-object people \
    --parent-record <record_id>

# Delete a note
attio notes delete <note_id>
```

---

### Phase 4: Schema Management (Objects & Attributes)

#### 4.1 Objects Commands
Manage object schemas (People, Companies, custom objects).

```bash
# List all objects
attio objects list

# Get object details
attio objects get <object_id_or_slug>

# Create custom object
attio objects create --api-slug "deals" --singular-noun "Deal" --plural-noun "Deals"

# Update object
attio objects update <object_id> --singular-noun "Opportunity"
```

#### 4.2 Attributes Commands
Manage attributes on objects.

```bash
# List attributes for an object
attio attributes list <object>

# Get attribute details
attio attributes get <object> <attribute_id>

# Create attribute
attio attributes create <object> --title "Priority" --type select

# Update attribute
attio attributes update <object> <attribute_id> --title "Urgency"

# List select options for a select attribute
attio attributes options <object> <attribute_id>

# Create select option
attio attributes add-option <object> <attribute_id> --title "High" --color "red"

# Update select option
attio attributes update-option <object> <attribute_id> <option_id> --title "Critical"

# List status options
attio attributes statuses <object> <attribute_id>

# Create status
attio attributes add-status <object> <attribute_id> --title "In Progress"

# Update status
attio attributes update-status <object> <attribute_id> <status_id> --title "Active"
```

---

### Phase 5: Search & Discovery

```bash
# Global search across multiple objects
attio search "query" [--objects people,companies] [--limit N]

# Search records (fuzzy matching on names, emails, domains, phones)
attio search records "john@example.com"

# Search within a specific object
attio search people "john"
attio search companies "acme"
```

---

### Phase 6: Workspace & Team Management

#### 6.1 Workspace Members
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

# Create comment
attio comments create <thread_id> --content "Great progress!"

# Get comment
attio comments get <comment_id>

# Delete comment
attio comments delete <comment_id>
```

---

### Phase 7: Webhooks Management

```bash
# List webhooks
attio webhooks list

# Get webhook details
attio webhooks get <webhook_id>

# Create webhook
attio webhooks create --target-url "https://example.com/webhook" \
    --subscriptions '["record.created", "record.updated", "task.created"]'

# Update webhook
attio webhooks update <webhook_id> --target-url "https://new-url.com/webhook"

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

### Phase 8: Advanced Features (Lower Priority)

#### 8.1 Meetings & Call Recordings (Beta)
```bash
# List meetings
attio meetings list [--limit N]

# Get meeting
attio meetings get <meeting_id>

# List call recordings for a meeting
attio recordings list <meeting_id>

# Get call recording
attio recordings get <recording_id>

# Get transcript
attio transcripts get <recording_id>
```

#### 8.2 Users Object
For SaaS products tracking their own users.

```bash
# List user records
attio users list [--limit N]

# Get user
attio users get <user_id>

# Create user
attio users create --data '{"...": "..."}'

# Assert user
attio users assert --match-attr user_id --data '{"...": "..."}'

# Delete user
attio users delete <user_id>
```

---

## Technical Implementation Details

### Dependencies (Cargo.toml)
```toml
[package]
name = "attio-cli"
version = "0.1.0"
edition = "2021"
description = "CLI for interacting with Attio CRM API"

[dependencies]
# CLI framework
clap = { version = "4", features = ["derive", "env"] }

# Async runtime
tokio = { version = "1", features = ["full"] }

# HTTP client
reqwest = { version = "0.11", features = ["json", "rustls-tls"] }

# JSON handling
serde = { version = "1", features = ["derive"] }
serde_json = "1"

# Error handling
thiserror = "1"
anyhow = "1"

# Configuration
toml = "0.8"
dirs = "5"

# Output formatting
tabled = "0.15"           # Table output
colored = "2"             # Colored terminal output
chrono = { version = "0.4", features = ["serde"] }

# Async traits
async-trait = "0.1"
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
- Authentication errors (401) - prompt to check API key
- Permission errors (403) - indicate missing scopes
- Not found errors (404) - clear resource not found message
- Validation errors (400/422) - display API error details
- Rate limiting (429) - implement exponential backoff
- Network errors - retry with backoff

### Output Formats

Support multiple output formats via `--output` flag:
- `table` (default): Human-readable table format
- `json`: Raw JSON for scripting
- `json-pretty`: Formatted JSON
- `yaml`: YAML format
- `ids-only`: Just IDs, one per line (for piping)

---

## Command Priority Summary

### Tier 1 (Must Have - Daily CRM Operations)
1. `attio config` - Setup and authentication
2. `attio auth whoami` - Verify connection
3. `attio people *` - People CRUD operations
4. `attio companies *` - Company CRUD operations
5. `attio records *` - Generic record operations
6. `attio search` - Find records quickly

### Tier 2 (Should Have - Workflow Management)
7. `attio lists *` - List management
8. `attio entries *` - Entry operations
9. `attio tasks *` - Task management
10. `attio notes *` - Note operations

### Tier 3 (Nice to Have - Administration)
11. `attio objects *` - Schema management
12. `attio attributes *` - Attribute configuration
13. `attio members *` - Team info
14. `attio webhooks *` - Integration hooks

### Tier 4 (Advanced - Specialized Use)
15. `attio threads/comments` - Collaboration
16. `attio meetings/recordings` - Call intelligence
17. `attio users *` - Product user tracking

---

## Next Steps

1. **Initialize Rust project** with Cargo
2. **Implement HTTP client** with authentication
3. **Build config management** system
4. **Implement People commands** first (most used)
5. **Add Companies commands**
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
