# Library File Guidance

Use this guide when creating new internal reference pages so they stay easy to
find, reuse, and maintain.

## Naming
- Prefix with the topic and format, e.g., `governance_playbook.md`,
  `ai_workflow_notes.md`, `runbook_incident_response.md`.
- If the file is a single-page brief, add `-sp` (single page) to the name, e.g.,
  `readiness_scoring-sp.md`.
- Keep names lowercase with underscores; avoid spaces.

## Location
- Store reusable knowledge under `docs/library/` (create if needed) grouped by
  domain: `ops/`, `cx/`, `gov/`, `data/`, `income/`.
- Product- or engagement-specific notes can live alongside code in
  `docs/` when tied to a release.

## Page Structure (single-page briefs)
- Title and last updated date at the top.
- "Purpose" (2–3 lines): why this page exists.
- "Scope" (1–2 lines): what is covered/not covered.
- "Core Content": bullets or short sections; include links to tools, SOPs, and
  owners.
- "Next Actions": 3–5 bullets that keep the page actionable.
- "Sources": links to authoritative docs or decisions.

## Content Hygiene
- Use short paragraphs and bullets; avoid long blocks of text.
- Add owners and review dates for policies or runbooks.
- When a decision changes, update the page and append a dated changelog entry at
  the bottom.

## Versioning
- For major updates, create a new file with a version suffix
  (e.g., `governance_playbook_v2.md`) and link from the prior version.

Following these patterns will keep the TekraQual library consistent and
searchable as new material is added.
