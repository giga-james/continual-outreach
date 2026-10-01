# ICP interview

Follow intent-first onboarding in `OUTREACH.md` at the distro root. If intent is unclear,
offer starting suggestions: explore a new/hypothetical idea, shape a campaign from a
product brief, or resume an existing campaign. Mention codebase context as an optional
supplement, not the presumed product. Do not inspect product source until selected.

When codebase context is explicitly requested, follow the context-reading procedure and
present a source-backed hypothesis. Otherwise begin from the user's chosen idea or brief:
“What are you building or considering, whose work should improve, and what would make a
conversation useful?” Ask about gaps instead of repeating known facts. Internal context
stays private unless approved for disclosure.

Then ask two or three questions at a time to resolve:

1. The painful task: what do they do manually, how often, what artifact results, and
   what evidence shows they personally own it? What makes a superficially similar person
   a poor fit? Who is a user, champion, buyer, or research collaborator?
2. Company stage/type, team, region/language if relevant, examples of excellent matches,
   competitive overlap, exclusions and previous contacts. Do not infer sensitive traits.
3. Public research sources, desired company diversity, research target vs send target,
   sender identity, approved pitch and specific call to action.
4. Channel, account, draft-only/manual/browser-assisted mode, existing sent/pending
   history, tracker location, limits, cohort size, pause window and success definition.

Write `icp.md` with must-have evidence, useful signals, disqualifiers, unknowns, buyer
path hypotheses and ranked examples. Once criteria and messaging direction are settled,
start the current agent’s browser session using `browser.md` and proceed to research
without asking the user to launch it. Save configuration plus an evidence-based sample
of 5–10 people with real notes. Present the concrete sample and pitch before asking for
missing sending authorization. Carry existing approval forward without re-asking.

Persist the campaign's four core settings in its own `campaign.json`: `icp` for the
current qualification criteria, `message_template` for the approved outreach template,
`tracker` for its export destination (including exact sheet/tab or file path), and
`channel` for the chosen outreach method (for example, `linkedin`). Keep `icp.md` as
supporting rationale and examples, aligned with the current configuration. Record the
sender account and approved scope in `authorization`. Do not copy these settings from
another campaign implicitly; an unset channel requires clarification before sending.

Initialize a new local campaign with draft-only defaults. If a sheet is wanted, use
available Google Sheets skills/connectors and honor the specified folder. Missing
connector access does not block local research; do not promise sheet sync until tested.

A first-run user saying only “start” authorizes the interview, not invitations.

During onboarding define the primary reward, observation window, profile segments and
exploration budget. Propose relevant reply within 14 days and 20% exploration as defaults;
explain acceptance is diagnostic and ask what makes a response genuinely useful.

Ask explicitly: “Which outreach method/account should we use, and where should I export
progress—Google Sheets, a local CSV, or another destination?” Discover available browser
and export capabilities before promising them. Save the exact path or sheet/folder URL,
perform a round-trip export check, and show the personalized messaging sample. For a
non-LinkedIn channel, preserve the same authorization and outcome rules but use that
channel's real recipient identity, limits, existing-contact status and tool workflow.
The bundled send ledger currently validates LinkedIn URLs; other channels require a
reviewed identity adapter before automated sending, not fabricated LinkedIn keys.

Resolve whether the user wants recurring work and its cadence from the conversation;
ask only if missing. When requested, complete agent-managed setup in `docs/scheduling.md`:
detect the runtime, configure and verify it, then report the scheduler and next run.
Do not hand off a configuration exercise to the user. If scheduling is not requested,
finish interactive onboarding without installing a background job.
