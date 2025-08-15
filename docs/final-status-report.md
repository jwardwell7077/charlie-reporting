# Status Reporting Guidelines

Concise, repeatable framework for communicating project status. Replace long "final reports" with small, high-signal updates.

## 1. Purpose

Provide stakeholders (engineering + non-technical) with a fast read that answers: Are we on track? What changed? What risks? What’s next?

## 2. When to Publish

| Cadence | Use Case | Length |
|---------|----------|--------|
| Daily (optional) | Rapid iterations | 3–5 bullets |
| Weekly | Standard progress | ≤ 1 screen (~120 lines max) |
| Milestone / Release | Scope complete | Extended w/ metrics |

## 3. Standard Structure

Recommended headings (omit if empty):

1. Status Summary (1–2 sentences, include traffic light: Green / Amber / Red)
2. Highlights (3–5 bullets: shipped value, decisions, measurable outcomes)
3. Metrics (only those that moved or matter)
4. Risks / Blockers (owner + mitigation)
5. Upcoming (next 3–5 concrete actions)
6. Decisions / Changes (architecture, scope, process)
7. Requests (help needed, approvals, external dependencies)

## 4. Status Summary Patterns

| State | Pattern Example |
|-------|-----------------|
| Green | "Green: Core ingestion stable; hourly aggregation validated on sample set." |
| Amber | "Amber: Loader idempotency partially implemented; risk of duplicates if restart mid-run." |
| Red | "Red: Excel generation failing on large dataset; blocking daily report endpoint." |

Keep summary objective; avoid marketing language.

## 5. Metrics Guidelines

Include only metrics that changed AND influence decisions:

- Throughput (files/hour, rows/hour)
- Accuracy (skipped vs processed files, validation error rate)
- Performance (ingest duration P50/P95)
- Quality (test coverage delta, failing tests count)
- Reliability (successful runs / total runs last 24h)

Format: metric → value → delta → brief note.

Example:

| Metric | Value | Δ | Note |
|--------|-------|---|------|
| Files ingested | 142 | +18 | New source enabled |
| Avg ingest time | 11.2s | -1.5s | Streaming parse |
| Validation errors | 3 | -2 | Stricter column map |

## 6. Risks & Blockers

Each item must have: Description → Impact → Mitigation → Owner.

Example:

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| No ingestion_log yet | Potential duplicate loads | Implement hash + table before scheduler | Dev A |

## 7. Upcoming / Forecast

List only work that is:

- Committed for next period OR
- Critical to unblock a risk.

Avoid speculative backlog items.

## 8. Decision Log (Inline ADR Lite)

Capture only decisions that alter scope, architecture, or external expectations. Format:

`[YYYY-MM-DD] Decision: <summary>. Context: <why>. Alternative(s): <brief>. Impact: <result>.`

## 9. Requests / Needs

Explicit asks (time, info, review). If none, omit section.

## 10. Tone & Style

| Principle | Guidance |
|-----------|----------|
| Brevity | 1 line per bullet; collapse adjectives |
| Objectivity | State facts + impact, not emotions |
| Traceability | Reference issue IDs / PRs when useful |
| Measurability | Prefer numbers over vague terms |
| Consistency | Same ordering each report |

## 11. Anti-Patterns (Avoid)

- Wall of text without structure
- Vanity metrics (lines of code, commit counts)
- Repeating unchanged metrics
- Entering solutioning details instead of outcomes
- Hiding risks until they escalate

## 12. Lightweight Template

```markdown
Status: Green | Amber | Red – <1 sentence rationale>

Highlights:
- <Delivered outcome>
- <Key decision>
- <Measured improvement>

Metrics:
| Metric | Value | Δ | Note |
|--------|-------|---|------|
| Files ingested | 142 | +18 | New ACQ feed |

Risks / Blockers:
| Item | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| ingestion_log missing | Possible duplicates | Implement hash table | JW |

Upcoming:
- Implement ingestion_log
- Add run_history tracking
- Prototype /generate/daily

Decisions:
- 2025-08-15: Reset to monolith; microservices overhead too high.

Requests:
- None
```

## 13. Final / Milestone Report Variation

Add a short "Outcome" section + 3 headline metrics + "Lessons" (max 5 bullets). Link to history for details instead of restating.

---
Use this file as the canonical standard; evolve only when a change improves clarity or reduces noise.

---

Legacy microservice-era final delivery report content removed (kept in git history) to keep this file focused solely on the lightweight status reporting standard.
