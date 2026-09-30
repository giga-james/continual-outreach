# Reliable scheduled runs

The repository owns campaign state, prompts and run reliability. The chosen agent owns
research and browser/connector interaction. Cron wakes it; cron does not send messages.

## Agent-managed setup

The agent owns scheduling setup. The user chooses whether to run continually and the
cadence; do not ask them to assemble a CLI command or edit `runner.json`.
Use existing preferences and authorization instead of asking again.

1. Inspect the current agent environment and existing campaign scheduler. Reuse an
   existing schedule. Prefer the current app's scheduler when it preserves the browser
   and connector access this campaign needs; do not configure a CLI runner in that case.
2. For a CLI-backed schedule, identify the current agent from session context and resolve
   its installed executable. Read that installed version's help for noninteractive mode
   and prompt input. Do not guess flags, select a different agent just because it is on
   PATH, or assume CLI tool access matches the desktop session.
3. Write `campaigns/<slug>/runner.json` yourself using an absolute executable path and
   an argv array. If needed, create a small private wrapper beside it to forward stdin
   or `{prompt_file}` in the documented format, run in the foreground and preserve exit
   status. Keep normal permissions; do not disable approvals or store credentials.
4. Probe the chosen command under the intended scheduler environment with a bounded,
   read-only prompt instead of the daily outreach prompt. Verify repository/campaign
   access, prompt delivery, exit status and the research/browser/export capabilities
   needed for this campaign. No invitations, messages or live tracker writes during
   setup validation. An exit code alone does not establish tool access.
5. Record the detected runtime, resolved command, capability checks and remaining gaps
   in the private checkpoint. Generate the cron entry with the bundled helper, then
   install it when recurring work has been requested. Preserve unrelated entries and
   verify the installed schedule, timezone and next run. Never create a second sender.

If runtime detection is ambiguous, ask only which agent to use. If authentication or a
required capability is missing, explain the specific action needed and retain research/
draft mode. If an unusual runtime cannot be configured from available documentation,
ask for its launch details as a fallback. Do not claim scheduling is active until verified.

## Runner reference

These are implementation details for the agent and advanced users. The agent generates
this private file after discovering the actual executable and supported arguments:

```json
{
  "argv": ["/absolute/path/to/discovered-agent-or-wrapper"],
  "timeout_seconds": 1800
}
```

The runner supplies the campaign prompt on stdin. For a filename argument, use
`{prompt_file}`. No CLI, browser tool or authentication is installed by this repository.
Cron's environment may differ from the interactive shell; use absolute paths and test
under that environment. Secrets belong in the existing authentication mechanism.

```sh
# Runs the campaign, potentially including authorized outreach; not a setup probe
python3 scripts/run_campaign.py --config campaigns/my-campaign/runner.json

# Prints the entry the agent installs after setup verification
python3 scripts/cron_entry.py --config campaigns/my-campaign/runner.json --hour 9
```

The second command prints an entry using the machine's cron timezone; it does not install
it. Use one scheduler per account. An app scheduler is a supported alternative when
browser capabilities are available only in the desktop session.

## Guarantees and limits

- POSIX file locking serializes scheduled campaigns within this checkout. Overlapping
  runs exit 75; locks release on process exit. Separate forks/machines are not coordinated.
- Each attempt has private `runs/<timestamp-id>/prompt.txt`, `output.log`, and
  `status.json`, including exit status and timestamps. Git ignores these campaign files.
- A timeout terminates the process group, records failure and exits 124. No automatic
  retries: a browser send could have happened before the failure. The next run must
  reconcile the reservation and tracker before sending.
- Process success means the agent exited successfully, not proof of sent invitations.
  Campaign status must still derive from verified browser and export evidence.
- A hard machine crash may leave a run marked running. Treat that as interrupted and
  reconcile it; do not infer that an external action did not occur.
- Linux/macOS POSIX runner; Windows users can use the app scheduler or an equivalent
  wrapper. The machine and authenticated tools must be available at run time.

Audit and research continue during send holds. Record updated response evidence and
selection plans, then send only when authorization, live status and the ledger permit.
