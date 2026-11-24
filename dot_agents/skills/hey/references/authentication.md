# Autenticación

Data commands use the credentials HEY already stores and refresh expiring OAuth tokens automatically. Run the requested data command without a login preflight.

If a data command returns exit code 3 with `"code": "auth"`, or fails with `could not read stored credentials`, authentication is unavailable to that process. On macOS under Codex, the sandbox can hide credentials that the HEY CLI stores in Keychain. Before reporting the task as blocked, use the harness's normal approval flow to retry `hey auth status --json` once with elevated sandbox permission. Limit the escalation to this one read-only command. If the response's `data.authenticated` is `true`, rerun only the exact `hey` command the user requested through a separate one-command approval. If `data.authenticated` is `false`, report the task as blocked and tell the user to run `hey auth login` in Terminal; do not run it for them unattended. If the status command fails instead, with a keyring error such as `exit status 36`, the login is not the problem and `hey auth login` will not fix it: report the task as blocked, relay the error's `hint`, and stop.

Never run the macOS `security` command to read Keychain contents, print or copy credentials, or move credentials into a file; never disable the sandbox globally; never set `HEY_NO_KEYRING=1` as an authentication workaround.

Piped, machine-output and non-TTY commands do not prompt for sign-in. When an agent harness runs commands under a PTY, set `HEY_NONINTERACTIVE=1` so a missing login returns the same actionable auth error instead of opening an interactive prompt.
