# PRD Doc Pro

**PRD Doc Pro** is an [Agent Skill](https://docs.cursor.com/context/skills) for Product Owners building **SaaS** product requirements. It pairs a **searchable knowledge base** (CSV + BM25) with a **PRD scaffold generator** so assistants can produce structured PRDs, user stories, metrics, and antipattern checks grounded in consistent playbooks.

---

## What it does

| Capability | Description |
|------------|-------------|
| **Product-type routing** | 13 SaaS archetypes (PLG, enterprise, API, AI, verticals, etc.) with recommended section order, personas, and metric focus. |
| **Section guidance** | 18 PRD sections with copy-ready templates, writing tips, and common mistakes. |
| **User stories** | 20 story categories with strong/weak examples, acceptance-criteria patterns, and SaaS context. |
| **Antipatterns** | 17 documented mistakes with bad vs good examples and concrete fixes. |
| **Metrics** | 16 SaaS metrics with definitions, formulas, benchmarks, and “anti-metric” warnings. |
| **Templates** | 9 PRD shapes (one-pager, full feature, epic, MVP, RFC, AI feature, API, etc.). |
| **Full scaffold** | One command that combines detection + sections + starter stories + metrics + antipatterns + template body. |

---

## How the system works

At a high level, the skill has three layers (similar in spirit to [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)):

```text
┌─────────────────────────────────────────────────────────────────┐
│  SKILL.md                                                        │
│  When to run it, workflow steps, domain table, checklists         │
└───────────────────────────────┬─────────────────────────────────┘
                                │ instructs the agent to run
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  scripts/search.py  →  scripts/core.py (BM25) + generator.py    │
│  • --generate-prd: assemble a full PRD outline                    │
│  • --domain <name>: search one knowledge domain                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ reads
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  data/*.csv                                                      │
│  Tabular knowledge: which columns are indexed vs returned        │
└─────────────────────────────────────────────────────────────────┘
```

### Search engine (`core.py`)

- Each **domain** maps to one CSV file and two column lists:
  - **Search columns** — tokenized and indexed for retrieval (BM25-style scoring).
  - **Output columns** — fields returned to the model (guidance, examples, templates).
- Queries are free text (e.g. `"PLG onboarding activation"`); the top rows per domain are ranked by relevance to the query.

### Generator (`generator.py`)

When you run `--generate-prd`, the generator:

1. Scores **product-type** rows against your description and picks the best SaaS subtype.
2. Pulls **section** hints, **user-story** starters, **metric** suggestions, and **antipattern** warnings using the same search engine.
3. Selects a **template** row matching the recommended PRD type.
4. Renders **ASCII** or **Markdown** output (CLI flag).

### Persistence (`--persist`)

Optional: writes `prd-docs/<project-slug>/MASTER.md` (and optionally `sections/<name>.md`) in the **current working directory**, so long-running work can use a master doc plus section overrides.

---

## Repository layout

```text
prd-doc-pro/
├── README.md                          ← this file
└── .cursor/skills/prd-doc-pro/
    ├── SKILL.md                       ← skill entry (instructions + triggers)
    ├── scripts/
    │   ├── search.py                  ← CLI
    │   ├── core.py                    ← BM25 + CSV_CONFIG
    │   └── generator.py               ← PRD assembly
    └── data/
        ├── product-types.csv
        ├── sections.csv
        ├── user-stories.csv
        ├── antipatterns.csv
        ├── metrics.csv
        └── templates.csv
```

---

## Requirements

- **Python 3** (scripts use `typing` patterns compatible with 3.9+; run with `python3`).

No extra pip packages — only the standard library.

---

## Installation

### Cursor (this repo)

The skill ships under **project** skills:

`.cursor/skills/prd-doc-pro/`

Cursor loads skills from that path when you work in this repository. The agent discovers it via the YAML `description` in `SKILL.md`.

### Claude CLI / global Claude skills

Copy the skill folder to your user skills directory so it applies to all projects:

```bash
mkdir -p ~/.claude/skills
cp -R .cursor/skills/prd-doc-pro ~/.claude/skills/
```

For **Claude CLI**, use absolute paths in `SKILL.md` for `search.py` (e.g. `~/.claude/skills/prd-doc-pro/scripts/search.py`) if you want the instructions to work from any working directory. The copy in this repo uses **relative** paths under `.cursor/...` suited for Cursor.

---

## How to use the skill

### With an AI assistant (recommended)

Describe the product or feature in natural language. Examples:

- *“Draft a PRD for a B2B SaaS enterprise onboarding flow.”*
- *“Give me user stories and acceptance criteria for CSV import.”*
- *“What success metrics fit a PLG freemium product?”*
- *“Review this problem statement for PRD antipatterns.”*

The assistant should follow `SKILL.md`: analyze the request, run `--generate-prd` for new PRDs, then use `--domain` searches to deepen specific sections.

### From the command line

From the **repository root**, paths below assume the bundled skill location.

**Full PRD scaffold:**

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py \
  "PLG SaaS onboarding and activation" \
  --generate-prd -p "MyProduct"
```

Markdown output:

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py \
  "Your description" \
  --generate-prd -p "MyProduct" \
  --format markdown
```

**Save to disk:**

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py \
  "Your description" \
  --generate-prd --persist -p "MyProduct"
# Optionally: --section "requirements" --output-dir /path/to/repo
```

**Search a single domain:**

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py \
  "problem statement quantified evidence" \
  --domain section -n 3
```

**JSON output (domain search only):**

```bash
python3 .cursor/skills/prd-doc-pro/scripts/search.py \
  "freemium conversion" \
  --domain metric \
  --json
```

### Knowledge domains (`--domain`)

| Domain | CSV | Use for |
|--------|-----|--------|
| `product-type` | `product-types.csv` | Which SaaS shape, template, section order, personas |
| `section` | `sections.csv` | Section content, tips, mistakes |
| `user-story` | `user-stories.csv` | Story patterns and AC examples |
| `antipattern` | `antipatterns.csv` | Bad/good examples and fixes |
| `metric` | `metrics.csv` | KPIs, formulas, benchmarks |
| `template` | `templates.csv` | Full markdown scaffolds |

---

## Extending the skill

1. **Add or edit rows** in the CSVs (keep header names stable, or update `CSV_CONFIG` in `core.py`).
2. **Add a new domain**: new CSV + new entry in `CSV_CONFIG` with `file`, `search_cols`, and `output_cols`.
3. **Regenerate** — no build step; the CLI reads CSVs at runtime.

Use a CSV editor or Python `csv` module with `QUOTE_ALL` for fields that contain commas or newlines.

---

## License and attribution

Knowledge in the CSVs synthesizes common product-management practice and public guides (e.g. PRD structure, user stories, metrics). Use and adapt for your team; cite internal policies and your own data when writing real PRDs.

---

## Quick reference — one-liners

```bash
# Scaffold
python3 .cursor/skills/prd-doc-pro/scripts/search.py "AI writing assistant B2B" --generate-prd -p "WriteAI" -f markdown

# Antipatterns
python3 .cursor/skills/prd-doc-pro/scripts/search.py "vague requirements no metrics" --domain antipattern

# Metrics for PLG
python3 .cursor/skills/prd-doc-pro/scripts/search.py "plg activation conversion" --domain metric
```

For the global Claude install, prefix with `~/.claude/skills/prd-doc-pro/scripts/search.py` instead.
