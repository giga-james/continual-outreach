# Continual profile learning

The core loop is observe → update profile beliefs → allocate the next batch → send
within limits → observe again. Rate-limit pauses are learning time: reconcile outcomes,
interpret feedback, research similar profiles and prepare new experiments. Do not raise
sending limits when a profile looks promising.

This is initially a delayed-feedback contextual-bandit approximation, not a full RL
agent or evidence that outreach causes product-market fit. Context is the pre-contact
profile; action is selecting a prospect/profile segment; reward is a relevant response.
The environment includes response delays and changing channel conditions. Conversations
may eventually support sequential policy learning, but this implementation uses segment
posteriors, not a trained contextual model.

## Reward and observation contract

Default primary reward: a relevant reply within 14 days that discusses the target
workflow or agrees to discuss it. A rejection, auto-reply or generic acceptance is not
that reward. Configure the rubric during onboarding. Track acceptance, any response,
qualified reply, booked chat and substantive feedback separately; do not combine them
into arbitrary points. Useful workflow feedback is the longer-term objective, so audit
whether optimizing replies actually produces it.

Freeze segment definitions, profile features and message version before contact. Begin
with a few interpretable segments based on workflow ownership and company context, not
sensitive personal traits. Do not create one segment per person or relabel responders to
make a segment look successful. Version changed segment definitions; do not pool
incompatible historical labels or messages without an explicit comparable analysis.

Use the complete contacted cohort, not just respondents. For quantitative updating,
count only outcomes with the same fully observed window; pending, missing coverage and
recent sends are censored. A checked, mature nonresponse is zero for response-within-
window, not proof that the person lacks pain. Late replies remain valuable qualitative
feedback and may inform a separately defined longer-window metric.

## Selection policy

Default proposal: 80% posterior-guided selection, 20% deliberate exploration. This is a
configurable campaign setting, not a platform recommendation. Bootstrap with balanced
exploration when there is no mature evidence. Never relax ICP must-haves or competitive
exclusions for exploration. Explore alternative qualified workflows/company types, and
avoid exhausting a single employer or treating correlated teammates as independent proof.

`scripts/select_batch.py` at repository root implements a simple Beta(1,1) posterior for
each frozen profile segment and Thompson sampling for the guided portion. The exploration
portion chooses uniformly among eligible segments, then people. It rounds exploration
up per batch. It is a reproducible planner, not a sender or causal-inference estimator.
Save the exact input, seed, output and any human/agent overrides with reasons before sends.
The script cannot prove eligibility or find aliases: deduplicate and verify upstream.

Input JSON contains `candidates` and `observations`. Candidates have `id`, `segment`,
`eligible` (true only after qualification, exclusion and contact checks). Observations
have `id`, frozen `segment`, `sent_at`, `observed_through`, and
`qualified_reply_within_window` (true/false/null). Use one latest consolidated row per
contact, not one row per audit; never count the same person twice. The Boolean must
reflect the stated window, not any eventual reply. All timestamps include timezones.

Example command:

```sh
python3 scripts/select_batch.py campaigns/example/selection-input.json --size 10 --exploration 0.2 --window-days 14 --seed 42
```

Keep a `policy.json` and dated selection inputs/outputs in the private campaign folder.
The selector's output is capped again by the send ledger and live platform state.
Do not send merely because the planner selected someone. Keep 7-day audit pauses even
when 14-day evidence is not mature; use the prior policy/exploration and explicitly
report that the evidence is insufficient, rather than promoting early responders alone.

## Close the loop

Every audit produces: profile-level denominators and rates, observation coverage,
uncertainty, valuable feedback themes, candidate-pool changes, policy version and the
next batch allocation. Prioritize profiles with demonstrated relevant conversations,
then research more people with the same observable work ownership. Keep exploratory
slots to challenge the current best hypothesis. Meaningful negative feedback should
narrow or revise the thesis; never conceal it by rewarding only engagement.
