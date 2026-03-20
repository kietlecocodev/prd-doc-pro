---
name: prd-doc-pro
description: "Product requirements intelligence for SaaS Product Owners. Creates PRD documents, user stories, acceptance criteria, success metrics, and stakeholder maps. 13 SaaS product types, 18 PRD sections with templates, 20 user story patterns, 17 antipatterns with bad/good examples, 16 SaaS metrics. Actions: create, write, draft, generate, review, improve, check PRD. Documents: PRD, product spec, RFC, epic brief, one-pager, MVP spec, AI feature PRD, API PRD. Sections: problem statement, user stories, acceptance criteria, success metrics, out of scope, launch plan, guardrail metrics, edge cases. Types: SaaS, B2B SaaS, PLG, developer platform, AI SaaS, enterprise SaaS, marketplace, vertical SaaS, fintech, healthcare, edtech, HR SaaS, analytics platform."
---

# PRD Doc Pro — Product Requirements Intelligence

Structured PRD guidance for SaaS Product Owners. Contains 13 SaaS product types, 18 section templates, 20 user story patterns, 17 antipatterns, 16 metrics, and 9 PRD templates. Powered by a BM25 knowledge base with a PRD scaffold generator.

## When to Apply

Use this skill when the user wants to:
- Create or draft a PRD, product spec, epic, MVP spec, or RFC
- Write user stories with acceptance criteria
- Define success metrics or OKRs for a feature
- Review a PRD for antipatterns and quality issues
- Find the right PRD template for their product type
- Understand what a specific PRD section should contain

---

## Prerequisites

Check Python 3 is available:
```bash
python3 --version
```

If not installed (macOS):
```bash
brew install python3
```

---

## How to Use This Skill

### Step 1: Analyze the Request

Extract from the user's message:
- **Product type**: What kind of SaaS? (B2B, PLG, API, enterprise, AI, fintech, etc.)
- **Feature scope**: Is this a full PRD, one section, or a quick user story?
- **Stage**: Early MVP, growth feature, enterprise expansion?
- **Output needed**: Full scaffold, section template, story examples, metrics, or antipattern check?

---

### Step 2: Generate PRD Scaffold (REQUIRED for new PRDs)

Always start with `--generate-prd` to get a complete scaffold with product-type-aware sections, starter user stories, metric recommendations, and antipatterns specific to this product type:

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py "<product description>" --generate-prd [-p "Project Name"]
```

**Example:**
```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py "B2B SaaS onboarding feature for enterprise customers" --generate-prd -p "SmartOnboard"
```

**What this returns:**
1. Detected SaaS product type + recommended template
2. Section order with writing guidance
3. 3 starter user stories with AC patterns
4. 4 recommended success metrics with benchmarks
5. Top 5 antipatterns to avoid
6. Full copy-ready PRD template scaffold

---

### Step 2b: Persist PRD for Long-Running Projects

To save the PRD for hierarchical retrieval across sessions:

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py "<description>" --generate-prd --persist -p "Project Name"
```

This creates:
- `prd-docs/<project>/MASTER.md` — Full PRD scaffold (global source of truth)

With a section-specific override:
```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py "<description>" --generate-prd --persist -p "Project Name" --section "requirements"
```

This also creates:
- `prd-docs/<project>/sections/requirements.md` — Section-level override

**Hierarchical retrieval:** When filling in a specific section, check `prd-docs/<project>/sections/<section>.md` first. If it exists, its rules override MASTER.md. Otherwise use MASTER.md exclusively.

---

### Step 3: Domain Searches for Specific Help

Use domain searches to get targeted knowledge for individual parts of a PRD:

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

| Need | Domain | Example Query |
|------|--------|---------------|
| PRD structure for my product type | `product-type` | `"enterprise saas compliance"` |
| How to write a specific section | `section` | `"problem statement evidence"` |
| User story examples with AC | `user-story` | `"billing subscription upgrade"` |
| Antipatterns to avoid | `antipattern` | `"missing metrics vague requirements"` |
| KPIs and success metrics | `metric` | `"activation plg freemium conversion"` |
| Which template to use | `template` | `"ai feature prd"` |

**Examples:**
```bash
# Get guidance on writing the problem statement section
python3 .cursor/skills/prd-doc-pro/scripts/search.py "problem statement user pain quantified" --domain section

# Get user story patterns for auth and onboarding
python3 .cursor/skills/prd-doc-pro/scripts/search.py "onboarding signup first value" --domain user-story

# Find the right metrics for a PLG product
python3 .cursor/skills/prd-doc-pro/scripts/search.py "plg freemium activation conversion" --domain metric

# Check for common antipatterns to avoid
python3 .cursor/skills/prd-doc-pro/scripts/search.py "requirements vague solution" --domain antipattern
```

---

### Step 4: Synthesize and Write

Use the scaffold + domain search results to write the PRD:

1. Start with the **Executive Summary** (write it last, put it first)
2. Write the **Problem Statement** with quantified evidence
3. Define **Target Personas** specifically (no generic 'user')
4. Set **Success Metrics** before writing requirements
5. Write **User Stories** with acceptance criteria (Given/When/Then or checklist)
6. List **Out of Scope** explicitly before starting requirements
7. Document **Edge Cases** for every user story
8. Add **Guardrail Metrics** (what must not regress)

---

## Available Domains

| Domain | Contents | Size |
|--------|----------|------|
| `product-type` | 13 SaaS subtypes with section order, personas, and metric focus | 13 rows |
| `section` | 18 PRD sections with templates, writing tips, and common mistakes | 18 rows |
| `user-story` | 20 story categories with good/bad examples, AC patterns, INVEST checks | 20 rows |
| `antipattern` | 17 antipatterns with bad examples, good examples, and fixes | 17 rows |
| `metric` | 16 SaaS metrics with formulas, benchmarks, and anti-metric warnings | 16 rows |
| `template` | 9 PRD template types with copy-ready markdown scaffolds | 9 rows |

---

## Quick Antipattern Checklist

Before delivering any PRD, verify these items:

### Problem & Goals
- [ ] Problem statement describes user pain, NOT a feature or solution
- [ ] Problem is quantified with numbers (%, counts, dollar impact)
- [ ] Goals are OKR-linked, not feature descriptions
- [ ] Success metrics have a baseline, target, and timeline

### User Stories
- [ ] Every story uses a specific persona, not 'As a user'
- [ ] Every story has a 'so that' clause
- [ ] No story is an epic (completable in 1 sprint)
- [ ] Every story has at least 3 acceptance criteria
- [ ] AC is testable (not 'works correctly' or 'is fast')

### Scope & Requirements
- [ ] Out of Scope section exists and is explicit
- [ ] Guardrail metrics listed (what must not regress)
- [ ] Edge cases documented for every user story
- [ ] Dependencies identified with owners and risk levels
- [ ] Rollback plan included in launch section

### Collaboration
- [ ] Engineering lead reviewed before finalization
- [ ] Changelog section maintained
- [ ] Open questions assigned with owners and due dates

---

## PRD Section Priority Reference

| Priority | Sections |
|----------|----------|
| CRITICAL | Executive Summary, Problem Statement, Target Users, Success Metrics, User Stories |
| HIGH | Guardrail Metrics, Functional Requirements, Non-Functional Requirements, Out of Scope, Edge Cases, Launch & Rollout |
| MEDIUM | Design & UX, Technical Considerations, Dependencies, Risks, Open Questions |
| LOW | Appendix, References |

---

## Example Workflow

**User request:** "Help me write a PRD for an AI writing assistant feature in our B2B SaaS tool"

### Step 1: Analyze
- Product type: AI/ML SaaS (B2B context)
- Template: AI Feature PRD
- Key concerns: model behavior, fallback, user control, privacy

### Step 2: Generate Scaffold
```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py "AI writing assistant B2B SaaS feature" --generate-prd -p "AI Writer"
```

### Step 3: Targeted Searches
```bash
# Section guidance for AI-specific sections
python3 .cursor/skills/prd-doc-pro/scripts/search.py "ai model behavior fallback confidence" --domain section

# User story patterns for AI features
python3 .cursor/skills/prd-doc-pro/scripts/search.py "ai suggest generate assist" --domain user-story

# AI SaaS metrics
python3 .cursor/skills/prd-doc-pro/scripts/search.py "ai feature adoption quality accuracy" --domain metric
```

### Step 4: Write
Use the scaffold, section guidance, and story patterns to write a complete PRD. The AI Feature PRD template includes: desired AI behavior spec, confidence + fallback handling, user control + override, privacy and data usage, quality metrics.

---

## Tips for Better Results

1. **Be specific** — `"PLG B2B SaaS activation onboarding"` beats `"app"`
2. **Name the stage** — include `"MVP"`, `"growth"`, `"enterprise"` in the query
3. **Search antipatterns early** — before writing, not after
4. **Iterate** — if first search results don't match, try different keywords
5. **Use persist** — for multi-session PRD work, save to `prd-docs/` for continuity
