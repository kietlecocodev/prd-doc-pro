# PRD Examples Index

## Good Examples (Gold Standard)

| # | Section | File | Key Lesson |
|---|---------|------|-----------|
| 01 | Problem Statement | `good/01-problem-statement.md` | Quantified pain with 3 failure points, $2.3M business impact, specific personas |
| 02 | User Stories + AC | `good/02-user-stories.md` | Specific persona, Given/When/Then AC, mobile edge cases, no implementation details |
| 03 | Success Metrics | `good/03-success-metrics.md` | Baseline→target→timeframe, guardrails, anti-metrics, mobile KPIs |
| 04 | Edge Cases (Mobile) | `good/04-edge-cases-mobile.md` | Network, device, permissions, data/sync, accessibility — exact behaviors specified |
| 05 | Launch & Rollout | `good/05-launch-rollout-mobile.md` | 5-phase rollout, numeric gates, rollback triggers, feature flags, app store timeline |
| 06 | Personas (Mobile) | `good/06-personas-mobile.md` | Named personas with device, usage pattern, frustration quotes, willingness to pay |
| 07 | Out of Scope | `good/07-out-of-scope.md` | Categorized exclusions with rationale, timeline, owner, data-driven decisions |

## Bad Examples (Annotated Anti-Patterns)

| # | Section | File | Key Lesson |
|---|---------|------|-----------|
| 01 | Problem Statement | `bad/01-problem-statement.md` | Solution-as-problem, unquantified, no personas, no business impact |
| 02 | User Stories | `bad/02-user-stories.md` | Generic persona, no AC, epic-sized, vague quality criteria |
| 03 | Success Metrics | `bad/03-success-metrics.md` | No baselines, no targets, no timeframes, unmeasurable, no guardrails |

## How to Use

- **When generating a PRD**: Reference good examples as templates for each section
- **When reviewing a PRD**: Compare against good examples to identify gaps
- **When training**: Show bad examples with annotations, then the corresponding good example
- **CLI**: `python3 search.py --example good/01-problem-statement` (coming in v2.1)
