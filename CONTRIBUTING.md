# Contributing to Continual Outreach

Contributions to the agent instructions, skills, research workflow, scheduling and
feedback loop are welcome. For a substantial change to the product direction or runtime
behavior, open an issue describing the problem and proposed approach first. Small fixes
can go straight to a pull request.

## Get started

1. Fork and clone the repository.
2. Read [AGENTS.md](AGENTS.md) for operating rules and [OUTREACH.md](OUTREACH.md) for the
   user-facing workflow. If using a coding harness, have it read those instructions too.
3. Create a branch for your change. Keep the change focused and preserve unrelated work.
4. Run the relevant checks and open a pull request against `main`.

Core scripts use Python 3.9+ and the standard library, with system timezone data. The
scheduled runner and its tests use POSIX file locking, so use Linux, macOS or a compatible
POSIX environment. You do not need a model API key, browser login or live campaign to run
the offline test suite.

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

The optional demo renderer needs Pillow; encoding the demo video also needs ffmpeg.
Its generation command is documented in `scripts/demo/render_walkthrough.py`.

## Find the right place

| Change | Start here |
| --- | --- |
| Agent behavior and onboarding | `OUTREACH.md`, `AGENTS.md` |
| Internal skills and workflow guidance | `.agents/skills/` |
| Campaign gates and outcome selection | `scripts/campaign.py`, `scripts/select_batch.py` |
| Workspace integration and recurring runs | `scripts/workspace.py`, `scripts/run_campaign.py`, `scripts/cron_entry.py` |
| Behavior checks | `tests/` |
| User documentation and walkthrough | `README.md`, `docs/`, `assets/` |

Keep the distro usable with different harnesses. Browser and connector capabilities
come from the user's environment; do not assume that a desktop tool exists in a scheduled
CLI session. Codebase context is optional and must be selected by the user. Existing
campaign state and authorization must survive changes to the workflow.

## Validate the change

For script changes, add or update tests for the behavior being changed and run the full
offline suite above. Useful cases include duplicate protection, uncertain sends, restart
recovery, campaign isolation and comparable feedback windows. Use temporary directories
and synthetic data, never a real campaign.

For instruction or skill changes, explain the scenario you checked and the expected
agent behavior. Review referenced paths and preserve the distinction between research,
sending authorization and scheduling. For docs-only changes, check links and formatting;
new unit tests are not necessary. Visually inspect changes to graphics or walkthroughs.

Do not send real invitations, messages or emails as a test. Do not install a real cron
job just to validate a script. If a change requires a live integration check, describe
what was checked and what remains unverified rather than claiming broader coverage.

## Keep campaign data private

Only reusable code, instructions and fictional examples belong in this repository.
Never commit prospect lists, private messages, replies, customer strategy, credentials,
campaign databases or run logs. Keep private state in the configured external directory
or ignored `campaigns/`, and inspect the staged diff before submitting.

Preserve the send gates: unknown outcomes stop sending until reconciled, export failures
hold further sends, and only one sender operates an account at a time. Do not introduce
hidden service endpoints, credential extraction or platform-restriction bypasses.

## Submit a pull request

Describe the problem, the resulting behavior and the validation performed. Include a
small before/after example when it makes the change easier to understand. Call out any
new dependency, state migration, behavior limitation or untested integration.

The active `main` ruleset requires one approving review from a code owner:
[@giga-james](https://github.com/giga-james). Authors cannot approve their own pull
requests. Maintainers
have configured bypass permissions, but contributions should follow the pull-request
review process. See [CODEOWNERS](.github/CODEOWNERS).

Before submitting:

- Keep the diff focused and update relevant documentation.
- Record the checks run and any limitations.
- Remove private data from examples, screenshots and logs.
- Explain changes to existing campaign state or operational guarantees.
