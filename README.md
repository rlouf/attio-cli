# Attio CLI

A command-line interface for [Attio](https://attio.com) CRM, designed for both humans and LLMs.

## Installation

```bash
cargo install --path .
```

## Configuration

Set your API key (get one from Attio workspace settings → Developers):

```bash
# Option 1: Environment variable
export ATTIO_API_KEY=your_api_key

# Option 2: Config file
attio config set api-key your_api_key
```

Verify it works:

```bash
attio whoami
```

## Usage

### Records

```bash
# List records
attio records list people
attio records list companies --limit 10
attio records list people --json | jq '.name'

# Get a record
attio records get people abc123

# Create a record
attio records create people '{"name": "John Doe", "email_addresses": ["john@example.com"]}'

# Create via stdin (useful for LLMs to avoid shell escaping)
echo '{"name": "John Doe"}' | attio records create people

# Update a record
attio records update people abc123 '{"name": "Jane Doe"}'

# Search
attio records search people "john"
attio records search companies "acme" --json
```

### Objects (Schema Discovery)

```bash
# List all objects (people, companies, custom objects)
attio objects list

# Get object details
attio objects get people
```

### Output Formats

- **Default**: Human-readable table
- **`--json`**: JSON for single records, JSONL for collections

```bash
# Table output
attio records list people

# JSON output (one record per line for collections)
attio records list people --json
attio records get people abc123 --json
```

## Design Decisions

### No Delete Operations

This CLI intentionally does not implement delete operations.

**Why?** This CLI is designed to be used as a tool by LLMs (like Claude). Delete operations are destructive and irreversible. Any "safety" mechanism we could implement (confirmation prompts, environment variables, flags) can be bypassed by an LLM that can execute shell commands.

**What to do instead:**
- Use the [Attio web interface](https://app.attio.com) to delete records
- Use the API directly if you need programmatic deletion with proper safeguards

This follows the principle of least privilege: the CLI provides read and write access, but not delete. This limits the blast radius of any mistakes or hallucinations.

### Stdin Support

All commands that accept JSON data can read from stdin:

```bash
echo '{"name": "John"}' | attio records create people
```

This is especially useful for LLMs, as it avoids shell escaping issues with complex JSON.

### JSONL for Collections

When using `--json`, collections are output as JSONL (one JSON object per line), not a JSON array. This enables streaming and piping:

```bash
attio records list people --json | jq -r '.email_addresses[0]'
attio records list people --json | head -5
```

## License

MIT
