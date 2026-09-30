# Export contract

During onboarding ask where the campaign should be tracked: an existing/new Google
Sheet (and folder), a local CSV path, or another available connector. Save the explicit
destination and do a read/write round trip before promising live export. Never create a
public share link by default. If the connector is absent, preserve local data and explain
what integration is needed; changing destination requires the user's preference.

Use stable prospect IDs across records. Export prospect identity, company, evidence,
qualification, competitive risk, approved draft, outreach status, sent date, cohort,
message version and independently observed outcomes. Keep sent messages immutable.
Preserve user-owned notes and decisions when updating existing destinations. Store audit
and policy versions separately so a new iteration does not rewrite history.

After every verified send or skip, upsert its row and verify the remote value before
another send. On export failure, save a local sync-pending checkpoint and hold sending.
For local CSV, use a temporary file plus atomic rename, UTF-8, and standard CSV quoting;
escape spreadsheet-formula prefixes in untrusted strings if spreadsheet consumption is
intended. Never concatenate CSV by hand. Google Sheets writes should use literal string
values for untrusted text, not formula interpretation.

The repository does not assume every agent has Google access. Use the agent's installed
connector/skill for native exports, supported browser tools only when appropriate, or a
local file exporter. Do not scrape authentication or call hidden service endpoints.
