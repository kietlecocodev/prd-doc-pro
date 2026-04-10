# PRD Doc Pro v2

**PRD Doc Pro** is an [Agent Skill](https://docs.cursor.com/context/skills) for Product Owners building **SaaS mobile product** requirements. It pairs a **searchable knowledge base** (CSV + BM25) with a **PRD scaffold generator**, **review engine**, and **mobile platform intelligence** so assistants can produce structured, high-quality PRDs grounded in consistent playbooks.

---

## What's New in v2

| Feature | v1 | v2 |
|---------|----|----|
| Product types | 13 | **24** (11 mobile-first archetypes) |
| User story patterns | 20 | **31** (11 mobile interaction stories) |
| Antipatterns | 17 | **25** (8 mobile-specific) |
| Metrics / KPIs | 16 | **28** (12 mobile KPIs) |
| **PRD Review Engine** | — | **Scores 0-100** with section-by-section rubric |
| **Platform Rules** | — | **20 iOS/Android** App Store & Play Store rules |
| **Mobile UX Patterns** | — | **20 patterns** with good/bad examples |
| **Gold Examples** | — | **10 annotated** PRD excerpts (7 good, 3 bad) |
| **Export** | — | **5 formats**: markdown, confluence, notion, html, text |
| **Platform Checklists** | — | **Auto-generated** iOS + Android checklists per feature |
| **Tests** | 0 | **26 tests** covering all modules |
| Total knowledge rows | 93 | **175+** |

---

## Quick Start

### Generate a Mobile PRD
```bash
python3 scripts/search.py "ride-sharing mobile app" \
  --generate-prd -p "GoRide" \
  --platform ios,android \
  -f markdown
```

### Review an Existing PRD
```bash
python3 scripts/search.py --review my-prd.md --strict --mobile
```

Output: scorecard with 0-100 score, section-by-section grades, top issues with fixes, and fill-in guidance for missing sections.

### Search Knowledge Base
```bash
# Mobile metrics
python3 scripts/search.py "crash rate retention DAU" --domain metric

# Platform compliance rules
python3 scripts/search.py "in-app purchase apple" --domain platform-rules

# Mobile UX patterns
python3 scripts/search.py "bottom sheet navigation" --domain mobile-ux

# Antipatterns
python3 scripts/search.py "permission spam offline" --domain antipattern
```

### Show Gold-Standard Examples
```bash
python3 scripts/search.py --list-examples
python3 scripts/search.py --example good/01-problem-statement
python3 scripts/search.py --example bad/02-user-stories
```

### Export to Other Formats
```bash
python3 scripts/search.py --export my-prd.md --export-format confluence
python3 scripts/search.py --export my-prd.md --export-format html --export-output prd.html
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  SKILL.md — Compact dispatch (~1.5K tokens)                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│  scripts/                                                     │
│  ├── search.py      — CLI entry point (all commands)          │
│  ├── core.py        — BM25 search engine + CSV config         │
│  ├── generator.py   — PRD scaffold assembly + mobile intel    │
│  ├── reviewer.py    — Review engine (scoring rubric)          │
│  ├── platform.py    — iOS/Android platform intelligence       │
│  └── exporter.py    — Format conversion (confluence/html/...) │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│  data/                                                        │
│  ├── product-types.csv    (24 types)                          │
│  ├── sections.csv         (18 sections)                       │
│  ├── user-stories.csv     (31 patterns)                       │
│  ├── antipatterns.csv     (25 antipatterns)                    │
│  ├── metrics.csv          (28 KPIs)                           │
│  ├── templates.csv        (9 templates)                       │
│  ├── platform-rules.csv   (20 iOS/Android rules)              │
│  ├── mobile-ux.csv        (20 UX patterns)                    │
│  ├── index.json           (tier-1 routing metadata)           │
│  └── details/examples/    (10 annotated PRD examples)         │
│      ├── good/  (7 gold-standard section examples)            │
│      └── bad/   (3 annotated anti-pattern examples)           │
└──────────────────────────────────────────────────────────────┘
```

---

## Knowledge Domains

| Domain | Rows | What It Contains |
|--------|------|-----------------|
| `product-type` | 24 | SaaS archetypes: B2B, PLG, enterprise, **mobile-first**, mobile fintech, mobile health, mobile social, mobile e-commerce, mobile edtech, mobile productivity, super app, AI mobile |
| `section` | 18 | PRD section templates with writing tips, priority, and common mistakes |
| `user-story` | 31 | Story patterns with good/bad examples, AC formats. **Mobile**: push, biometric, offline, camera, location, deep link, gestures, search, paywall, app update |
| `antipattern` | 25 | PRD mistakes with annotated examples and fixes. **Mobile**: permission spam, notification abuse, offline ignorance, desktop-first design, no rollback plan, no performance budget, platform differences ignored, no app store compliance |
| `metric` | 28 | KPIs with formulas, benchmarks, anti-metric warnings. **Mobile**: D1/D7/D30 retention, crash-free rate, app store rating, push opt-in, cold start time, session length, app size, deep link conversion, uninstall rate, IAP conversion, widget usage, background sync |
| `template` | 9 | Copy-ready PRD markdown scaffolds |
| `platform-rules` | 20 | iOS App Store + Google Play Store guidelines that affect PRD requirements |
| `mobile-ux` | 20 | Mobile UX patterns: navigation, loading, interaction, onboarding, search, layout, dark mode, accessibility |

---

## Review Engine

The review engine scores PRDs 0-100 against a rubric with checks for:

- **Problem Statement** (15 pts): Quantified pain, no solution leaking, user + business impact
- **Target Users** (10 pts): Specific named personas with context and motivation
- **Goals** (10 pts): Outcome-based (not feature-based), measurable
- **Success Metrics** (15 pts): Baselines, targets, timeframes, formulas, mobile KPIs
- **User Stories** (20 pts): Specific personas, so-that clauses, testable AC, sprint-sized
- **Out of Scope** (5 pts): Explicit exclusions with rationale
- **Guardrails** (8 pts): Metrics that must not regress
- **Edge Cases** (7 pts): Error states, mobile-specific scenarios
- **Design** (5 pts): Wireframes or design principles referenced
- **Launch** (5 pts): Phased rollout, feature flags, rollback criteria

### Grading Scale
| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | EXCELLENT | Ready for engineering |
| 75-89 | GOOD | Minor gaps, addressable quickly |
| 60-74 | NEEDS WORK | Significant gaps, iterate before handoff |
| 40-59 | WEAK | Major sections missing or inadequate |
| 0-39 | CRITICAL | Not ready — needs fundamental rework |

---

## Requirements

- **Python 3.9+** (stdlib only — no pip packages)

---

## Installation

### Cursor
The skill ships under `.cursor/skills/prd-doc-pro/`. Cursor loads it automatically.

### Claude Code
```bash
mkdir -p ~/.claude/skills
cp -R .cursor/skills/prd-doc-pro ~/.claude/skills/
```

---

## Running Tests

```bash
cd .cursor/skills/prd-doc-pro/tests
python3 test_core.py -v
```

26 tests covering: search engine, all 8 domains, review engine, scoring, exporter, platform intelligence.

---

## License

Knowledge in the CSVs synthesizes common product-management practice and public guides. Use and adapt for your team.
