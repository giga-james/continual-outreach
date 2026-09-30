<h1 align="center">Continual Outreach</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Agent-Independent-6366f1" alt="Agent independent">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Status-Experimental-f4a7c3" alt="Experimental">
  <a href="https://x.com/kunggaochicken"><img src="https://img.shields.io/badge/Follow-%40kunggaochicken-000000?logo=x&logoColor=white" alt="Follow @kunggaochicken on X"></a>
</p>

<p align="center"><strong>Bring your agent. Find your customers. Learn from every batch.</strong></p>

A reusable outreach workflow for **any agent that can read files and use the required tools**:
Codex, Claude Code, or your preferred agent. Fork the repository, start a conversation,
and let your agent interview you about your ideal customers, outreach channel, messaging
and tracking destination.

Between batches, it uses useful responses to refine the next set of profiles while
preserving room to explore. The repository supplies shared instructions, campaign state
and reliable scheduling scripts. You supply the agent and its authenticated tools.

<p align="center">
  <a href="#start">Start</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#the-feedback-loop">Feedback loop</a> ·
  <a href="docs/scheduling.md">Scheduling</a> ·
  <a href="docs/exports.md">Exports</a>
</p>

## Start

1. **Fork and clone** this repository.
2. **Open your agent** in the cloned directory.
3. **Start the interview:**

> Read AGENTS.md and start a new outreach campaign. Interview me.

The agent helps you define:

| Decision | What you work out together |
| --- | --- |
| Ideal customers | Product, painful workflow, ownership evidence and disqualifiers |
| Outreach | Channel, account, existing contacts, authorization and sending budget |
| Messaging | Your voice, verified work references and call to action |
| Tracking | Google Sheets, local CSV or another available export connector |
| Learning | What counts as a useful response, observation window and exploration budget |

It saves a private campaign, researches a sample, shows personalized drafts and checks
export access. Sending begins only within your authorization; that authorization carries
forward within its scope.

**No specific agent runtime is required.** [AGENTS.md](AGENTS.md) is the shared entry
point. [CLAUDE.md](CLAUDE.md) points Claude to it; agents with skill discovery can load
[the outreach skill](.agents/skills/outreach/SKILL.md). Every instruction is ordinary
Markdown, so agents without a skill loader can read the same workflow directly.

## Architecture

![User flow: fork and open any agent, complete an interview, research and draft, send authorized outreach through connected tools, track outcomes, then audit and tune the next batch. A scheduler wakes the agent; a private ledger gates sends.](assets/architecture.svg)

The agent performs research and interacts with the chosen channel. Local scripts keep
state and enforce operational gates. A scheduler wakes the agent; it does not send
messages itself. During sending pauses, the agent audits outcomes and prepares the next
batch.

| Component | Responsibility |
| --- | --- |
| Agent instructions | Interview, research, qualification, messaging and recovery |
| Your agent and tools | Web research, supported computer use and export connectors |
| Campaign ledger | Duplicate protection, reservations, send caps and audit holds |
| Selection planner | Rank qualified segments using observed outcomes and exploration |
| Scheduled runner | Deliver prompts, serialize local runs, enforce timeouts and save logs |
| Private campaign and exports | Preserve prospects, exact messages, outcomes and policy changes |

## The feedback loop

**Research → qualify → personalize → send → observe → audit → tune.**

Success means a useful response defined during onboarding. Acceptance, relevant replies,
booked conversations and substantive feedback remain separate outcomes, so optimizing
for connections does not silently replace learning from customers.

The initial policy uses **80% posterior-guided selection and 20% exploration** among
qualified profiles. [The planner](scripts/select_batch.py) uses segment-level Thompson
sampling with Beta posteriors. It learns only from comparable, fully observed windows;
recent and unknown outcomes remain unobserved rather than becoming failures.

The agent interprets conversation feedback, researches similar profiles and records
selection changes. This is a delayed-feedback bandit approximation, not a trained model
over individual prospects. The planner proposes a batch; authorization and send gates
still decide whether it can run.

## Scheduling

After onboarding, configure your agent command in the private campaign's `runner.json`.
The runner supplies a prompt on stdin or through `{prompt_file}`, uses a checkout-wide
lock, records each run and enforces a timeout. Failed runs are not automatically retried.

```sh
python3 scripts/run_campaign.py --config campaigns/my-campaign/runner.json
python3 scripts/cron_entry.py --config campaigns/my-campaign/runner.json --hour 9
```

The second command **prints a cron entry; it does not install it**. Use one scheduler
per account. An agent app's scheduler is also supported. See
[Scheduling](docs/scheduling.md) for configuration, environment requirements and recovery.

## Capabilities and limits

- **Bring your tools.** Web research, authenticated computer use and export connectors
  are supplied by your agent environment. Cloning this repository does not install them.
- **Channel support is explicit.** The included send guard supports LinkedIn profile
  identity. Other channels can be researched and drafted, but need a tested identity
  adapter before automated sending.
- **Pacing is not platform permission.** LinkedIn prohibits third-party automated
  activity. Use manual sending when appropriate and stop on platform warnings.
- **Scheduled access can differ.** A cron-launched CLI may lack desktop browser tools.
  The POSIX runner supports Linux/macOS; unavailable capabilities produce a checkpoint.
- **Local locks are local.** Reconcile account-wide sends and serialize senders across
  campaigns and machines. An uncertain send stops further sending until reconciled.

## Private state and tracking

Campaign configuration, prospect records, messages, replies, audits and run logs live
in ignored `campaigns/`. Keep a private backup: these files are not included in your fork.
The repository contains only a [generic, draft-mode example](examples/campaign.json).

Exports use stable IDs and are verified after each send or skip. If synchronization
fails, sending pauses until the tracker is repaired. See [Exports](docs/exports.md).

```sh
# Inspect your campaign
python3 scripts/campaign.py --campaign campaigns/my-campaign status

# Run the offline checks; no real outreach is sent
python3 -m unittest discover -s tests -v
```

---

[Agent instructions](AGENTS.md) · [Outreach skill](.agents/skills/outreach/SKILL.md) ·
[Scheduling](docs/scheduling.md) · [Exports](docs/exports.md)
