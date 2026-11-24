# Discovery-first workflow

For each task:

1. Infer the deepest plausible leaf command from the user's words.
2. Unless its arguments and flags are already established by a tool result in this conversation, read that leaf's help before running it:
   ```bash
   hey <group> <subcommand> --agent --help
   ```
3. If the leaf does not exist, read its nearest parent group. Use root help only when the top-level group itself is unclear:
   ```bash
   hey <group> --agent --help   # fallback
   hey --agent --help           # last resort
   hey commands --json          # every command with its agent_notes
   ```
4. Treat the leaf's `short`, `long`, `agent_notes` and `flags` as the source of truth. Do not guess positional arguments, flags, accepted values, or limits.
5. Run with an explicit output mode, then read structured errors before deciding what to do next.

Leaf help is cheap; root help and `hey commands --json` print the whole catalog and are not. Global flags (`--json`, `--jq`, `--quiet`, `--account`, `--stats`) apply wherever a command supports them.
