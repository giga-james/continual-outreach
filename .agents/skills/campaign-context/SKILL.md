---
name: campaign-context
description: Build a campaign brief from a user's idea and explicitly selected context such as GitHub repositories, documents, interview notes or local files. Used internally by the Continual Outreach agent when formulating or revising a campaign.
metadata:
  internal: true
---

# Campaign context

The user's intended product or idea is authoritative. The current directory is just
where the agent is running. Do not infer that its codebase is the product.

Start from the stated goal. If unclear, offer to explore a new/hypothetical idea, shape a
campaign from a brief, or continue existing outreach. Ask one useful opening question;
do not present a setup questionnaire. Mention that selected repos, docs or notes can
supplement the conversation, but they are optional. Proceed without them when unnecessary.

## Use selected sources

Accept multiple context sources: GitHub repositories or files, local projects, websites,
documents, interviews, or text supplied in the conversation. Read only sources the user
selects or authorizes. A selected repo is relevant evidence, not permission to disclose
its contents or to replace the product idea with whatever its code implements.

Use available repository, document or browser tools. For a GitHub repo, start with its
README and relevant product docs, then inspect only the implementation needed to answer
campaign questions. For a local repo, follow its own agent instructions. Don't execute
source, change product code, clone into the host project, or inspect credentials for
context gathering. If access is unavailable, record that gap and continue from the brief.

For each selected source, record its path/URL, why it matters, revision/date when known,
verified observations, uncertainties and whether information is public or internal.
Keep this in the private campaign's context.md once state is needed. Preserve the user's
chosen sources across sessions; don't silently add the current workspace to that list.

## Return a brief, not an architecture tour

Summarize the product hypothesis, likely users, painful repeated work, qualification
signals and unknowns. Tie inferences to their sources. Distinguish current functionality,
aspirational ideas and observed customer evidence. Ask the user to correct material gaps,
then hand the brief to the outreach interview and research workflow.

Separate internal findings from approved public claims. Do not send private code,
roadmaps, customer identities or metrics to web searches, outreach or shared trackers.
Use generic research terms from the agreed ICP; clarify disclosure scope only when it
matters to the proposed action. No chosen context source authorizes sending messages.
