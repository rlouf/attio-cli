# CLI UX Improvement Plan

## Goals

Improve the Attio CLI in four areas:

1. Help and examples for deeper commands
2. Consistent, polished error handling
3. Safer and clearer auth/config storage
4. More operator-shaped workflows on top of the existing resource model

## Current Gaps

### Help

- Top-level help is now grouped, but deeper command help is still thin.
- Many commands that require JSON or resource IDs do not show task-oriented examples where the user needs them.
- The README has useful examples, but they are too far away from the command surface.

### Errors

- Input and usage errors are raised as `click.ClickException`.
- API failures are raised separately as `AttioError`.
- That split makes the CLI feel inconsistent and limits how actionable API errors are.
- Authentication failures are not as helpful as missing-config failures.

### Auth and Config

- Auth is API-key based only.
- `ATTIO_API_KEY` takes precedence over local config.
- Local config is stored as plain JSON on disk.
- That is acceptable for a developer tool, but weak from a UX and security perspective.

### Information Architecture

- The current command surface is mostly resource-shaped, which is good for completeness and scripts.
- Some operations still feel too close to the raw API instead of matching how operators think about tasks.

## Proposed Changes

## Phase 1: Normalize Runtime Errors

Make runtime failures feel like one coherent CLI instead of a mix of layers.

Changes:

- Replace the current bare `AttioError` pattern with a structured error type.
- Include fields such as:
  - `status_code`
  - `message`
  - `hint`
  - `details` when relevant
- Catch API errors once at the CLI boundary and render them as polished Click-style failures.
- Keep JSON/input validation errors consistent with the same tone and formatting.

Desired outcomes:

- `401`: explain how to set `ATTIO_API_KEY` or run `attio config set api-key <key>`
- `403`: explain that the key is valid but access is denied
- `404`: explain what kind of resource was not found when possible
- `422`: show validation guidance and suggest inspecting the target first
- `429`: explain retry behavior clearly

Why first:

- This is the highest-ROI polish change.
- It improves every command without changing command names or workflows.

## Phase 2: Improve Auth Storage and UX

Keep environment-based auth for automation, but make local auth safer and clearer.

Changes:

- Continue to prioritize `ATTIO_API_KEY`.
- Prefer OS keychain storage via `keyring` for saved credentials.
- Fall back to config-file storage only when keychain support is unavailable.
- Make the auth source visible in config/help output.
- Consider expanding config commands to:
  - `config login`
  - `config logout`
  - `config show`

Desired outcomes:

- Better local security without hurting scripts or CI.
- Clearer understanding of where the CLI is reading credentials from.

## Phase 3: Add Examples to Command Help

Move important usage guidance closer to the commands themselves.

Changes:

- Add a custom Click command/group help renderer that supports command metadata like:
  - `examples`
  - `see_also`
  - short workflow hints
- Render an `Examples:` section in `--help` for commands that need it most.
- Prioritize commands that currently require guesswork:
  - `records create`
  - `records update`
  - `entries create`
  - `entries update`
  - `attributes create`
  - `attributes update`
  - `attributes add-status`
  - `attributes update-status`
  - `tasks create`

Desired outcomes:

- Users can solve common tasks from `--help` without opening the README.
- JSON-heavy commands become much easier to use correctly on the first try.

## Phase 4: Add Workflow-Oriented Entry Points

Preserve the current API-shaped commands, but add operator-friendly paths for common tasks.

Principle:

- Keep existing commands stable for scripts and completeness.
- Add workflow aliases or top-level verbs for common jobs.

Examples:

- `attio find people "john"`
- `attio show people <id>`
- `attio add-to-list <list> --record-id <id>`
- `attio note add ...`
- `attio task add ...`

Desired outcomes:

- Better usability for humans without breaking the current command surface.
- A clearer distinction between scripting primitives and operator workflows.

## Implementation Order

Recommended order:

1. Phase 1: normalize errors
2. Phase 2: improve auth storage and auth UX
3. Phase 3: add examples to command help
4. Phase 4: add workflow-oriented aliases

## Design Notes

- Do not remove or rename the current resource-based commands during these phases.
- Prefer additive changes first.
- Use the README for broader tutorials, but keep task-critical examples in command help.
- Keep machine-readable behavior stable:
  - `--json`
  - JSONL for collections
  - stdin / `--data` / `--data-file`

## Immediate Next Step

Start with Phase 1 by introducing a structured API error model and routing all API failures through consistent CLI output.
