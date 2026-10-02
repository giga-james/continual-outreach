# Sending and recovery

Requirements: Python 3.9+ with timezone data, a supported authenticated computer-use
browser tool, explicit campaign send authorization and a reconciled account-wide ledger
or an explicit, bounded user override for incomplete historical counts.
No browser credentials are stored here. Google Sheets connectors are optional for a new
local campaign, required when the chosen campaign uses Sheets as its shared tracker.

Before each run:

1. Read config, checkpoint, live tracker and ledger. Reconcile sends made outside this
   campaign too. Never set `reconciled_at` merely because the local DB loaded. Record
   evidence for the account send count and its coverage. If history is incomplete,
   explain the gap and offer a bounded override; honor approval already in the session.
   Persist `history_override` with `approved: true`, `user_instruction`, `approved_at`,
   `expires_at` and scope. Keep `reconciled_at` unchanged. The helper waives only the
   reconciliation-age gate until expiry; duplicate, reservation and other gates remain.
2. Check pause, platform warnings, daily/rolling caps and cohort audits. Initial pauses
   do not expire into authorization. Review `authorization` and `send_authorized`.
   If only a campaign-configured cap blocks sending, offer an explicit override with a
   maximum number of additional requests and a batch boundary. Do not present this cap
   as a LinkedIn limit. If already approved, proceed without repeat confirmation.
3. Verify recipient identity, current role, work, qualification and competitive risk.
   Inspect their live profile: skip existing connections or pending requests. No InMail,
   withdrawal or follow-up DM unless separately requested.
4. Prepare the approved note in the UI. Inspect actual recipient, text and limit.
5. Reserve immediately before the final Send, then click once. Verify a sent toast or
   Pending state. Resolve the reservation, update the tracker and verify the write before
   proceeding. On uncertainty, resolve as `unknown`, stop sends and inspect later.

For an approved cap override, record the user's instruction, approval time, original
caps, additional-request ceiling, target cohort and expiry in the private campaign
configuration and checkpoint. After reconciling account history (or recording an explicit
history override), temporarily set the
effective caps to the observed daily/rolling counts plus the approved additional ceiling;
track that ceiling across restarts. Clear only the cap-related hold, retain other gates,
and restore the original caps when the batch completes, expires or is stopped. Do not
delete history, rotate cohorts, fabricate audits or mark incomplete history reconciled
to activate an override. A cap override is not authorization for new recipients, revised
messages, a recurring schedule, or bypassing a platform warning or restriction.
When historical counts are waived, label counters as local rather than account totals
and limit additional sends using the recorded local baseline and approved batch ceiling.

Commands from repository root (replace the campaign directory and URLs):

```sh
python3 scripts/campaign.py --campaign campaigns/example status
python3 scripts/campaign.py --campaign campaigns/example import-history campaigns/example/history.json
python3 scripts/campaign.py --campaign campaigns/example reserve 'https://www.linkedin.com/in/person/' --cohort c001 --message-file campaigns/example/note.txt
python3 scripts/campaign.py --campaign campaigns/example resolve 'https://www.linkedin.com/in/person/' sent --evidence 'Observed Pending on the verified profile at …'
python3 scripts/campaign.py --campaign campaigns/example audit c001 continue --report campaigns/example/audits/c001.md
```

`reserve` is transactional: one outstanding attempt blocks all other sends, including a
second process. It also refuses previously recorded profiles. `resolve` accepts `sent`,
`unknown`, `already_pending`, `already_connected`, or `not_sent`; evidence is mandatory.
Unknown attempts remain blocking and never expire automatically. Resolve to `not_sent`
only after visible proof, not a timeout. That profile still remains blocked in the ledger;
any deliberate retry needs a reviewed data migration, not deletion to bypass the guard.
Historical sends use a JSON array of `profile, sent_at, cohort, message, evidence`.
Timestamps must include an offset. Import is idempotent, conflicts fail atomically.
For date-only history, preserve date precision separately and use a conservative end-of-
day timestamp only after that day ends. Until then do not send if the total is uncertain.

Config fields are described by `examples/campaign.json`. `reconciled_at` must be within
24 hours; daily counters use configured timezone, rolling counters use exact UTC time.
All campaigns using one account must share one ledger or import all account sends and
serialize operations. This is local crash protection, not distributed exactly-once
sending: the browser and database cannot commit atomically. A stopped/crashed reservation
must be investigated, never automatically retried. Back up campaign data privately.

When a cohort reaches its limit, the helper requires the observation wait to pass and a
subsequent audit with decision `continue`. An explicit pause decision on any cohort also
holds sending. Do not generate a token audit to unlock the gate. Use a new cohort ID
once an audit is recorded. The helper checks limits; the skill checks relevance and consent.

If the tracker write fails after a send, persist the verified send locally and mark sync
pending; do not send more until sync is repaired. For an existing campaign, import the
full live sent history before authorizing local reservations, unless the user explicitly
approves the bounded incomplete-history exception above.

Persist one active cohort ID across daily runs; never assign a new cohort to bypass its
observation window. The helper rejects rotation while any prior cohort is unaudited.
Post-reservation `already_pending` and `already_connected` consume quota conservatively,
because an uncertain attempt may have sent successfully. Pre-send skips belong in the
prospect tracker and do not need reservations. Audit decisions are append-only events;
the latest decision per cohort controls the gate. Keep dated full audit reports too.
