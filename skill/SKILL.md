---
name: managing-attio-crm
description: Manages Attio CRM data via the attio-cli command-line tool. Use when the user wants to work with CRM records (people, companies), lists, entries, tasks, notes, or workspace settings. Supports listing, creating, updating, and searching CRM data.
---

# Attio CLI

A command-line interface for the Attio CRM API. Delete operations are intentionally not implemented for safety.

## Configuration

The API key must be set via environment variable:

```bash
export ATTIO_API_KEY="your-api-key"
```

## First step

Start by running:

```bash
attio --llm
```

That built-in guide is the source of truth for:
- command inventory
- identifier conventions
- structured JSON input rules
- common discovery and update workflows
- known limitations

Use `attio <group> --help` for exact signatures after reading `attio --llm`.

## Commands Reference

### Authentication

```bash
attio whoami  # Verify API key and show workspace info
attio --llm   # Print the built-in machine-oriented operating guide
```

### Records (people, companies, custom objects)

```bash
# List records
attio records list people
attio records list companies --limit 10

# Retrieve a specific record
attio records retrieve people <record-id>

# Create a record (prefer stdin, --data, or --data-file)
echo '{"email_addresses": ["john@example.com"], "name": "John Doe"}' | attio records create people
attio records create people --data-file record.json

# Update a record
echo '{"name": "Jane Doe"}' | attio records update people <record-id>

# Search records
attio records search people "john" --limit 5
```

### Lists and Entries

```bash
# List all lists (pipelines)
attio lists list

# Retrieve list details
attio lists retrieve <list-slug>

# Update a list
attio lists update <list-slug> --data '{"name": "Enterprise Pipeline"}'

# List entries in a list
attio entries list <list-slug>

# Add a record to a list
attio entries create <list-slug> --record-id <record-id>

# Update entry values
echo '{"status": "active"}' | attio entries update <list-slug> <entry-id>
```

### Tasks

```bash
# List tasks
attio tasks list

# Create a task
attio tasks create "Follow up with client" --deadline "2025-02-01"

# Mark as completed
attio tasks update <task-id> --completed true
```

### Notes

```bash
# List notes for a record
attio notes list --parent-object people --parent-record-id <record-id>

# Create a note
attio notes create --title "Meeting Notes" --parent-object people --parent-record-id <record-id> --content "Discussion points..."
```

### Attributes (schema)

```bash
# List attributes for an object
attio attributes list people

# List attributes for a list
attio attributes list <list-id> --target lists

# Retrieve attribute details
attio attributes retrieve people email_addresses

# List select options
attio attributes options <object> <attribute>

# List status options
attio attributes statuses <object> <attribute>
```

### Workspace

```bash
# List workspace members
attio members list

# List webhooks
attio webhooks list
```

## Output Formats

- **Default**: Human-readable table
- **--json**: JSON for single items, JSONL for collections

```bash
# Get JSON output for scripting
attio records list people --json | head -1 | jq '.id.record_id'
```

## Guidelines

1. Start with `attio --llm`, then use `attio <group> --help` for exact signatures
2. Prefer `--json` when IDs or structured confirmation are needed
3. Prefer stdin, `--data`, or `--data-file` for structured JSON payloads
4. Record IDs and list IDs are UUIDs returned by the API
5. Use object slugs: `people`, `companies`, or custom object slugs
6. Delete operations are not available (by design for safety)
