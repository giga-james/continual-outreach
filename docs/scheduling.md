# Reliable scheduled runs

The repository owns campaign state, prompts and run reliability. The chosen agent owns
research and browser/connector interaction. Cron wakes it; cron does not send messages.

## Configure a runner

Finish interactive onboarding first. In the private campaign directory, create
`runner.json` with a noninteractive agent command as an argv array:

```json
{
  "argv": ["/absolute/path/to/your-agent-wrapper"],
  "timeout_seconds": 1800
}
```

The runner supplies the campaign prompt on stdin. If your agent instead needs a filename,
use `{prompt_file}` in an argument. The wrapper should invoke your installed Codex,
Claude or other agent in its documented noninteractive mode, forward stdin or that file,
run in the foreground, return the actual exit code, and use its normal permission settings. Check that version's
help; do not add flags that disable approvals. No CLI, browser tool or authentication is
installed by this repository. Secrets belong in your existing authentication mechanism,
not argv or tracked files. Cron's environment may differ from your interactive shell.
Use absolute executable paths and test under that environment.

```sh
python3 scripts/run_campaign.py --config campaigns/my-campaign/runner.json
python3 scripts/cron_entry.py --config campaigns/my-campaign/runner.json --hour 9
```

The second command prints an entry for review, using the machine's cron timezone. It
does not install it. Install through your scheduler only when requested, preserving
unrelated entries and checking for existing campaign scheduling. Use one scheduler per
account. An agent app scheduler is a supported alternative when browser capabilities
are available only in the desktop session.

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
