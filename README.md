# Attio CLI

A command-line interface for interacting with the [Attio CRM API](https://developers.attio.com/).
The Python package name is `attio`.

## Installation

```bash
pip install attio
```

## Configuration

Set your API key via environment variable (recommended):

```bash
export ATTIO_API_KEY="your-api-key"
```

Or save it for local CLI use:

```bash
attio config login
# or
attio config login "your-api-key"
```

Saved credentials prefer the system keychain when available and fall back to the config file otherwise.
Use `attio config show` to see the active auth source and preferred local storage backend.
`attio config set api-key "your-api-key"` remains supported for backward compatibility.

## Usage

### Check authentication

```bash
attio whoami

# Print a machine-oriented usage guide for AI agents
attio --llm
```

### Structured input

Commands that accept structured JSON now support four input styles:

1. `--data '<json>'`
2. `--data-file payload.json`
3. `--data-file -` or plain piped stdin
4. legacy positional JSON for backward compatibility

Preferred patterns:

```bash
# Pipe JSON via stdin
echo '{"name": "Jane Doe"}' | attio records create people

# Read JSON from a file
attio records update people <record-id> --data-file record-update.json

# Pass JSON explicitly with a flag
attio lists update <list-id> --data '{"name": "Enterprise Pipeline"}'
```

### Records

```bash
# List people
attio records list people

# Get a specific record
attio records retrieve people <record-id>

# Create a record (JSON as argument)
attio records create people --data '{"email_addresses": ["john@example.com"], "name": "John Doe"}'

# Create a record (via stdin)
echo '{"email_addresses": ["john@example.com"]}' | attio records create people

# Update a record
attio records update people <record-id> --data '{"name": "Jane Doe"}'

# Update a record from a file
attio records update people <record-id> --data-file record-update.json

# Search records
attio records search people "john"

# List records with filter/sort JSON from files
attio records list people --filter-file people-filter.json --sort-file people-sort.json

# List list entries linked to a record
attio records entries people <record-id>

# List values for a record attribute
attio records values people <record-id> region
```

### Lists & Entries

```bash
# List all lists (pipelines)
attio lists list

# Update a list (JSON as flag, file, or stdin)
attio lists update <list-id> --data '{"name": "Enterprise Pipeline"}'
attio lists update <list-id> --data-file list-update.json

# List entries in a list
attio entries list <list-slug>

# List entries with filter/sort JSON from files
attio entries list <list-slug> --filter-file entry-filter.json --sort-file entry-sort.json

# Add a record to a list
attio entries create <list-slug> --record-id <record-id>

# Add a record to a list with entry values
echo '{"status": "active"}' | attio entries create <list-slug> --record-id <record-id>

# Update entry values
attio entries update <list-slug> <entry-id> --data-file entry-update.json

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

# Create an attribute with JSON input
echo '{"title": "Stage", "type": "status", "api_slug": "stage"}' | attio attributes create <list-id> --target lists
attio attributes create people --data-file attribute.json

# Update an attribute
attio attributes update people region --title "Sales Region" --slug sales_region
attio attributes update people region --data '{"description": "Used for sales reporting"}'

# List attribute options or statuses, including archived values
attio attributes options people region --show-archived
attio attributes statuses <list-id> stage --target lists --show-archived

# Update an option or status with richer payloads
attio attributes update-option people region <option-id> --archived true
attio attributes update-status <list-id> stage <status-id> --target lists --celebration-enabled true

# Provide nested status timing JSON from a file
attio attributes update-status <list-id> stage <status-id> \
  --target lists \
  --target-time-in-status-file target-time.json
```

### Tasks

```bash
# List tasks
attio tasks list

# Create a task
attio tasks create "Follow up with client" --deadline "2025-01-30"

# Create a task with assignees/linked records from files
attio tasks create "Follow up with client" \
  --assignees-file assignees.json \
  --linked-records-file linked-records.json

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
2. **Structured input**: Use `--data`, `--data-file`, or piped stdin for JSON payloads
3. **JSONL output**: Easy to parse programmatically
4. **No delete operations**: Intentionally omitted for safety
5. **Agent guide**: `attio --llm` prints a compact operating guide for AI agents

```bash
# LLM-friendly: pipe JSON via stdin
echo '{"name": "Acme Corp"}' | attio records create companies --json

# Print the built-in agent guide
attio --llm
```

## Development

The repository now has a standard local verification workflow:

```bash
# Run the full test suite
make test

# Run lint, formatting, and type checks through pre-commit
make check

# Run the full local verification pass
make verify
```

If you prefer not to use `make`, the underlying commands are:

```bash
uv run --with pytest pytest -q tests
uvx pre-commit run --all-files
uv run --with-editable . --with ty --with pytest ty check src tests
uvx ruff check src tests
uvx ruff format --check src tests
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
