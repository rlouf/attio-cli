# Attio CLI

A command-line interface for interacting with the [Attio CRM API](https://developers.attio.com/).

## Installation

```bash
pip install attio-cli
```

## Configuration

Set your API key via environment variable (recommended):

```bash
export ATTIO_API_KEY="your-api-key"
```

Or save it to the config file:

```bash
attio config set api-key "your-api-key"
```

## Usage

### Check authentication

```bash
attio whoami
```

### Records

```bash
# List people
attio records list people

# Get a specific record
attio records retrieve people <record-id>

# Create a record (JSON as argument)
attio records create people '{"email_addresses": ["john@example.com"], "name": "John Doe"}'

# Create a record (via stdin - better for LLMs)
echo '{"email_addresses": ["john@example.com"]}' | attio records create people

# Update a record
attio records update people <record-id> '{"name": "Jane Doe"}'

# Search records
attio records search people "john"

# List list entries linked to a record
attio records entries people <record-id>

# List values for a record attribute
attio records values people <record-id> region
```

### Lists & Entries

```bash
# List all lists (pipelines)
attio lists list

# Update a list (JSON as argument or via stdin)
attio lists update <list-id> '{"name": "Enterprise Pipeline"}'

# List entries in a list
attio entries list <list-slug>

# Add a record to a list
attio entries create <list-slug> --record-id <record-id>

# List values for a list entry attribute
attio entries values <list-slug> <entry-id> status
```

### Attributes

```bash
# List attributes for an object
attio attributes list people

# List attributes for a list
attio attributes list <list-id> --target lists

# Create an attribute with flags
attio attributes create people --title "Region" --type select --slug region

# Create an attribute with raw JSON
echo '{"title": "Stage", "type": "status", "api_slug": "stage"}' | attio attributes create <list-id> --target lists

# Update an attribute
attio attributes update people region --title "Sales Region" --slug sales_region

# List attribute options or statuses, including archived values
attio attributes options people region --show-archived
attio attributes statuses <list-id> stage --target lists --show-archived

# Update an option or status with richer payloads
attio attributes update-option people region <option-id> --archived true
attio attributes update-status <list-id> stage <status-id> --target lists --celebration-enabled true
```

### Tasks

```bash
# List tasks
attio tasks list

# Create a task
attio tasks create "Follow up with client" --deadline "2025-01-30"

# Mark task as completed
attio tasks update <task-id> --completed true
```

### Notes

```bash
# List notes for a record
attio notes list --parent-object people --parent-record-id <record-id>

# Create a note
attio notes create --title "Meeting Notes" --parent-object people --parent-record-id <record-id>
```

## Output Formats

By default, output is formatted as a human-readable table. Use `--json` for machine-readable output:

- Single items: JSON object
- Collections: JSONL (one JSON object per line)

```bash
# Human-readable table
attio records list people

# JSON Lines (for piping/scripting)
attio records list people --json

# Pipe to jq
attio records list people --json | jq -r '.id.record_id'
```

## LLM Usage (Claude Skill)

This CLI is designed to be usable by LLMs:

1. **Discoverability**: Use `--help` on any command
2. **Stdin support**: Pipe JSON to avoid shell escaping issues
3. **JSONL output**: Easy to parse programmatically
4. **No delete operations**: Intentionally omitted for safety

```bash
# LLM-friendly: pipe JSON via stdin
echo '{"name": "Acme Corp"}' | attio records create companies --json
```

## Commands

| Command | Description |
|---------|-------------|
| `attio whoami` | Show workspace info |
| `attio config` | Manage configuration |
| `attio objects` | List/get object schemas |
| `attio records` | CRUD for records |
| `attio lists` | Manage lists |
| `attio entries` | Manage list entries |
| `attio tasks` | Manage tasks |
| `attio notes` | Manage notes |
| `attio attributes` | Manage object and list attributes |
| `attio members` | List workspace members |
| `attio webhooks` | Manage webhooks |

## License

MIT
