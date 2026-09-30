# Qualification and personalization

Start or resume the current agent’s computer-use session via `browser.md`. Browser-led
research is the default; available search tools can accelerate source discovery.

Search primary company posts, project pages, contribution statements, public
repositories and relevant vendor customer stories. Follow
vendor → customer → named builder → their work → verified professional identity.
Do not confuse a customer's logo with a named person's ownership. For each promising
source, open the original work and establish the contribution before finding the person's
professional profile. Use the profile to resolve identity and contact eligibility; a
profile match alone does not establish qualification.

Use one JSON object per prospect in `prospects.jsonl`:
`id, name, company, role, profile_url, work_name, source_urls, checked_at, evidence,
qualification, competitive_risk, risk_reason, status, draft, message_version`.
Evidence should distinguish person-level responsibility, team-level work and inference.
Suggested qualification labels: verified practitioner, plausible author, unverified.
Unknown identity stays unverified; only verified practitioners matching the ICP enter
sending. A lead list may retain clearly labeled hypotheses without counting them as
qualified. Coauthorship, title and popularity alone are insufficient.

Look for concrete evidence that the person owns the workflow named in the campaign's
ICP: artifacts they created, processes they maintain and problems they describe.
Distinguish a hands-on champion from a budget owner. Verify company affiliation as
current, historical or unknown, and assess competitive overlap against the campaign's
explicit exclusions at the product level.

Deduplicate by normalized LinkedIn profile, person aliases and organization/work evidence.
Identical names alone are not enough to merge people. Prefer organizational breadth over
adding every coauthor. Exclusions propagate across a person's discovered projects.

Draft from the authorized template using a short, specific and verified work reference.
Never invent familiarity, job responsibilities or a project name. Count characters
against the visible channel limit; shorten the work reference without changing meaning.
If it cannot fit, ask about a revised template rather than silently changing the pitch.
Record exclusions and uncertainty instead of forcing the research target.
