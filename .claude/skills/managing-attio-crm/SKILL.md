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

## Commands Reference

### Authentication

```bash
attio whoami  # Verify API key and show workspace info
```

### Records (people, companies, custom objects)

```bash
# List records
attio records list people
attio records list companies --limit 10

# Get a specific record
attio records get people <record-id>

# Create a record (pipe JSON via stdin to avoid shell escaping)
echo '{"email_addresses": ["john@example.com"], "name": "John Doe"}' | attio records create people

# Update a record
echo '{"name": "Jane Doe"}' | attio records update people <record-id>

# Search records
attio records search people "john" --limit 5
```

### Lists and Entries

```bash
# List all lists (pipelines)
attio lists list

# Get list details
attio lists get <list-slug>

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

# Get attribute details
attio attributes get people email_addresses

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

1. Always pipe JSON data via stdin to avoid shell escaping issues
2. Record IDs and list IDs are UUIDs returned by the API
3. Use object slugs: `people`, `companies`, or custom object slugs
4. Delete operations are not available (by design for safety)
