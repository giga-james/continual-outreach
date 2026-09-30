# Continual Outreach

This repository runs research and outreach campaigns through the agent the user chooses
(Codex, Claude, or another agent). These are canonical agent-independent instructions. When the user says
“start”, “continue”, or asks for prospecting, load `.agents/skills/outreach/SKILL.md`.
On first start, interview the user before creating a campaign. Do not assume example configuration defines their ICP or authorizes any communication.

Campaign data belongs in ignored `campaigns/`. Code and generic instructions may be
committed; prospect records, messages, replies and credentials must not be committed.
Never read browser cookies or credentials. Use the provided computer-use/browser tools
for browser interactions, and connector APIs for spreadsheets. No hidden HTTP endpoints,
headless social-network scripts or detection-evasion mechanisms.

A user-authorized campaign can proceed without repeat approvals within its scope. New
campaigns start in draft mode. Unknown send results must be reconciled before another
send. Platform warnings stop sending; a scheduler is not authorization to bypass them.
One sender process per account, across all campaigns and machines. The local ledger
cannot see another campaign's sends: reconcile the whole account before sending.

For code changes run `python3 -m unittest discover -s tests -v`. Do not send real
invitations as a test. Preserve existing campaign data and automation identifiers.

Read the skill as ordinary Markdown if native skill discovery is unavailable. `CLAUDE.md`
points here; other agents can be explicitly told to read this file. Onboarding must cover
ICP, outreach method/account, export destination, message/CTA and authorization before
sends. Use `docs/exports.md` for tracking and `docs/scheduling.md` for unattended runs.
Do not assume a desktop browser is available in a cron-launched CLI. Missing capabilities
mean research/draft mode, with a concrete needs-input checkpoint, not fake completion.

Scheduling setup is agent-owned: detect the current runtime, generate its configuration,
probe scheduled capabilities without sending, and install/verify the requested schedule.
Follow `docs/scheduling.md`. Ask users for cadence or missing access, not routine CLI
configuration. Reuse existing schedulers and authorization.
