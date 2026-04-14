---
name: prd-doc-pro
description: "PRD intelligence engine for SaaS mobile products. Creates, reviews, scores, and exports PRD documents. 24 SaaS product types (11 mobile-first), 35 sections, 31 user story patterns, 25 antipatterns, 28 metrics (12 mobile KPIs), 20 platform rules (iOS/Android), 20 mobile UX patterns, 10 gold-standard examples. Actions: create, draft, generate, review, score, improve, export PRD. Documents: PRD, product spec, RFC, epic brief, one-pager, MVP spec, AI feature PRD, API PRD, mobile PRD. Sections: problem statement, user stories, acceptance criteria, success metrics, guardrail metrics, edge cases, mobile platform checklist, app store compliance. Types: SaaS, mobile SaaS, PLG, fintech, health, marketplace, e-commerce, social, edtech, productivity, super app, AI mobile."
---

# PRD Doc Pro v2 — Product Requirements Intelligence

## When to Apply
Use when the user wants to: create/draft/review/score/improve/export a PRD, write user stories, define metrics, check PRD quality, or get mobile platform guidance.

## Commands

| Intent | Command |
|--------|---------|
| New PRD | `search.py "<description>" --generate-prd -p "Name" [--platform ios,android] [-f markdown]` |
| Review PRD | `search.py --review <file> [--strict] [--mobile]` |
| Domain search | `search.py "<query>" --domain <domain>` |
| Export | `search.py --export <file> --export-format confluence\|notion\|html\|text` |
| Show example | `search.py --example good/01-problem-statement` |
| List examples | `search.py --list-examples` |
| Visualize flow | See `flow-visualizer/SKILL.md` — generates FigJam/Miro diagrams from PRD content |

## Domains
`product-type` (24), `section` (18), `user-story` (31), `antipattern` (25), `metric` (28), `template` (9), `platform-rules` (20), `mobile-ux` (20)

## Workflow

### New PRD
1. Analyze: Extract product type, platform, scope, stage
2. Generate: `--generate-prd` detects type, returns sections + stories + metrics + antipatterns + mobile checklist
3. Fill in: Use `fill_in_required` guidance for each section — ask user for specific data (baselines, personas, business impact)
4. Review: `--review` scores 0-100, flags issues with fixes
5. Iterate: Fix issues, re-review until score ≥80

### Section Deep Dive
```bash
python3 search.py "problem statement quantified evidence" --domain section
python3 search.py "push notification biometric auth" --domain user-story
python3 search.py "crash rate retention mobile" --domain metric
python3 search.py "in-app purchase apple ios" --domain platform-rules
python3 search.py "bottom sheet navigation" --domain mobile-ux
python3 search.py "permission spam notification abuse" --domain antipattern
```

### Review Existing PRD
```bash
python3 search.py --review path/to/prd.md --strict --mobile
```
Output: scorecard with section scores, top issues with fixes, missing sections with fill-in guidance, and suggested search commands.

## Key Rules
- **Never skip fill-in prompts**: If review shows missing data (baselines, personas, business impact), ask the user to provide it before finalizing
- **Mobile-first**: For any mobile product, always use `--platform ios,android` — the generator auto-adds platform checklists, compliance rules, and UX patterns
- **Score gate**: A PRD scoring below 60 is not ready for engineering. Fix issues first.
- **Examples**: Show `--example good/<section>` when user needs inspiration for a section

## Gold-Standard Examples
| Section | Good | Bad |
|---------|------|-----|
| Problem Statement | `good/01-problem-statement` | `bad/01-problem-statement` |
| User Stories + AC | `good/02-user-stories` | `bad/02-user-stories` |
| Success Metrics | `good/03-success-metrics` | `bad/03-success-metrics` |
| Edge Cases (Mobile) | `good/04-edge-cases-mobile` | — |
| Launch & Rollout | `good/05-launch-rollout-mobile` | — |
| Personas | `good/06-personas-mobile` | — |
| Out of Scope | `good/07-out-of-scope` | — |

## Quick Antipattern Checklist
Before delivering any PRD:
- [ ] Problem describes pain, NOT a feature (no solution leaking)
- [ ] Problem quantified with numbers (%, $, counts, time)
- [ ] Every story uses specific persona (never "As a user")
- [ ] Every story has "so that" clause + ≥3 testable AC
- [ ] Metrics have baseline → target → timeframe → measurement tool
- [ ] Guardrail metrics defined (what must not regress)
- [ ] Out of scope section exists with ≥3 items and rationale
- [ ] Edge cases documented for each story (including mobile: offline, permissions, interruptions)
- [ ] For mobile: platform checklist complete (iOS + Android requirements)
- [ ] For mobile: app store compliance verified
- [ ] Launch plan includes phased rollout + rollback triggers + feature flags

## Flow Visualization
After generating or reviewing a PRD, offer to visualize key flows using the `flow-visualizer` sub-skill. Say: "Want me to visualize this as a flow diagram in FigJam?" Supports user journeys, decision trees, swimlanes, system architecture, and rollout plans. See `flow-visualizer/SKILL.md` for full details.
