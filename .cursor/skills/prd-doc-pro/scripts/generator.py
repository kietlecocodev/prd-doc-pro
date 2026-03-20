#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Doc Pro Generator — assembles a complete PRD scaffold from domain knowledge.

Equivalent to ui-ux-pro-max's design_system.py — takes a product description
and produces a ready-to-fill PRD template with the right structure, sections,
user story starters, metric suggestions, and antipattern warnings.
"""

from pathlib import Path
from typing import Optional, Tuple
from core import search, search_domain, load_all_rows, MAX_RESULTS


def _truncate(text: str, max_chars: int = 250) -> str:
    return text[:max_chars] + "..." if len(text) > max_chars else text


def _box(title: str, content: str, width: int = 72) -> str:
    border = "─" * width
    lines = [f"┌{border}┐", f"│  {title:<{width - 2}}│"]
    for line in content.splitlines():
        lines.append(f"│  {line:<{width - 2}}│")
    lines.append(f"└{border}┘")
    return "\n".join(lines)


def generate_prd(
    query: str,
    project_name: Optional[str] = None,
    output_format: str = "ascii",
    persist: bool = False,
    section: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> str:
    """
    Generate a complete PRD scaffold for the given product description.

    Steps:
    1. Detect the closest SaaS product type
    2. Get recommended sections and their templates
    3. Suggest 3 starter user stories with AC patterns
    4. Recommend key metrics
    5. List the top 5 antipatterns to avoid for this product type
    6. Render the assembled PRD scaffold
    """
    project_label = project_name or "Your Product"

    # ── 1. Detect product type ──────────────────────────────────────────
    pt_result = search_domain(query, "product-type", max_results=1)
    product_type_row = pt_result["results"][0] if pt_result["results"] else {}
    product_type = product_type_row.get("Product Type", "SaaS B2B (General)")
    recommended_template = product_type_row.get("PRD Template", "full-feature-prd")
    recommended_depth = product_type_row.get("Recommended Depth", "4-8 pages")
    personas = product_type_row.get("Primary Personas", "Admin User, End User")
    sections_order = product_type_row.get("Sections Order", "")
    key_considerations = product_type_row.get("Key Considerations", "")
    oos_mistakes = product_type_row.get("Common Out-of-Scope Mistakes", "")

    # ── 2. Get recommended sections ─────────────────────────────────────
    sec_result = search_domain(query + " " + product_type, "section", max_results=5)
    sections = sec_result["results"]

    # ── 3. Get user story starters ──────────────────────────────────────
    story_result = search_domain(query, "user-story", max_results=3)
    stories = story_result["results"]

    # ── 4. Get metric suggestions ───────────────────────────────────────
    metric_result = search_domain(query + " " + product_type, "metric", max_results=4)
    metrics = metric_result["results"]

    # ── 5. Get top antipatterns to watch ────────────────────────────────
    ap_result = search_domain(query, "antipattern", max_results=5)
    antipatterns = ap_result["results"]

    # ── 6. Get template scaffold ─────────────────────────────────────────
    template_result = search_domain(recommended_template + " " + query, "template", max_results=1)
    template_row = template_result["results"][0] if template_result["results"] else {}
    template_markdown = template_row.get("Markdown Template", "").replace("\\n", "\n")

    # ── Render ──────────────────────────────────────────────────────────
    if output_format == "markdown":
        return _render_markdown(
            project_label, product_type, recommended_template, recommended_depth,
            personas, sections_order, key_considerations, oos_mistakes,
            sections, stories, metrics, antipatterns, template_markdown
        )
    else:
        return _render_ascii(
            project_label, product_type, recommended_template, recommended_depth,
            personas, sections_order, key_considerations, oos_mistakes,
            sections, stories, metrics, antipatterns, template_markdown
        )


def _render_ascii(project, product_type, template, depth, personas, sections_order,
                  considerations, oos, sections, stories, metrics, antipatterns,
                  template_markdown):
    out = []
    w = 72

    out.append("═" * w)
    out.append(f"  PRD DOC PRO — {project}")
    out.append("═" * w)

    # Product type
    out.append(f"\n◆ PRODUCT TYPE DETECTED: {product_type}")
    out.append(f"  Template:  {template}")
    out.append(f"  Depth:     {depth}")
    out.append(f"  Personas:  {personas}")

    if sections_order:
        out.append(f"\n◆ RECOMMENDED SECTION ORDER")
        for i, s in enumerate(sections_order.split(" > "), 1):
            out.append(f"  {i:>2}. {s.strip()}")

    if considerations:
        out.append(f"\n◆ KEY CONSIDERATIONS FOR THIS PRODUCT TYPE")
        for line in considerations.split(". "):
            if line.strip():
                out.append(f"  • {line.strip().rstrip('.')}")

    # Sections
    if sections:
        out.append(f"\n◆ TOP SECTION GUIDANCE (from knowledge base)")
        for sec in sections:
            name = sec.get("Section Name", "")
            priority = sec.get("Priority", "")
            tips = _truncate(sec.get("Writing Tips", ""), 160)
            mistakes = _truncate(sec.get("Common Mistakes", ""), 120)
            out.append(f"\n  [{priority}] {name}")
            if tips:
                out.append(f"  Tips:     {tips}")
            if mistakes:
                out.append(f"  Avoid:    {mistakes}")

    # User stories
    if stories:
        out.append(f"\n◆ SUGGESTED USER STORY STARTERS")
        for i, s in enumerate(stories, 1):
            category = s.get("Story Category", "")
            example = _truncate(s.get("Good Story Example", ""), 180)
            ac = _truncate(s.get("AC Example", ""), 200)
            out.append(f"\n  [{i}] {category}")
            out.append(f"  Story: {example}")
            if ac:
                out.append(f"  AC:    {ac.split(chr(10))[0]}")

    # Metrics
    if metrics:
        out.append(f"\n◆ RECOMMENDED SUCCESS METRICS")
        for m in metrics:
            name = m.get("Metric Name", "")
            category = m.get("Category", "")
            benchmark = _truncate(m.get("Target Benchmark", ""), 80)
            why = _truncate(m.get("Why It Matters", ""), 120)
            out.append(f"\n  {name} [{category}]")
            out.append(f"  Benchmark: {benchmark}")
            out.append(f"  Why:       {why}")

    # Antipatterns
    if antipatterns:
        out.append(f"\n◆ TOP ANTIPATTERNS TO AVOID")
        for ap in antipatterns:
            name = ap.get("Antipattern Name", "")
            section = ap.get("Affects Section", "")
            symptom = _truncate(ap.get("Symptom", ""), 100)
            fix = _truncate(ap.get("Fix", ""), 100)
            out.append(f"\n  ✗ {name} (in: {section})")
            out.append(f"    Symptom: {symptom}")
            out.append(f"    Fix:     {fix}")

    # Out-of-scope warning
    if oos:
        out.append(f"\n◆ COMMON OUT-OF-SCOPE MISTAKES")
        out.append(f"  Watch out: {oos}")

    # Template scaffold
    if template_markdown:
        out.append(f"\n◆ PRD TEMPLATE SCAFFOLD (copy and fill in)")
        out.append("─" * w)
        out.append(template_markdown[:1500] + ("..." if len(template_markdown) > 1500 else ""))

    out.append("\n" + "═" * w)
    return "\n".join(out)


def _render_markdown(project, product_type, template, depth, personas, sections_order,
                     considerations, oos, sections, stories, metrics, antipatterns,
                     template_markdown):
    lines = []

    lines.append(f"# PRD Doc Pro — {project}")
    lines.append(f"\n## Product Type: {product_type}")
    lines.append(f"- **Template:** {template}")
    lines.append(f"- **Depth:** {depth}")
    lines.append(f"- **Personas:** {personas}")

    if sections_order:
        lines.append(f"\n## Recommended Section Order")
        for i, s in enumerate(sections_order.split(" > "), 1):
            lines.append(f"{i}. {s.strip()}")

    if considerations:
        lines.append(f"\n## Key Considerations")
        for line in considerations.split(". "):
            if line.strip():
                lines.append(f"- {line.strip().rstrip('.')}")

    if sections:
        lines.append(f"\n## Section Guidance")
        for sec in sections:
            name = sec.get("Section Name", "")
            priority = sec.get("Priority", "")
            tips = sec.get("Writing Tips", "")
            mistakes = sec.get("Common Mistakes", "")
            lines.append(f"\n### {name} `[{priority}]`")
            if tips:
                lines.append(f"**Tips:** {_truncate(tips, 200)}")
            if mistakes:
                lines.append(f"**Avoid:** {_truncate(mistakes, 150)}")

    if stories:
        lines.append(f"\n## Suggested User Story Starters")
        for s in stories:
            category = s.get("Story Category", "")
            example = s.get("Good Story Example", "")
            ac = s.get("AC Example", "").replace("\\n", "\n")
            lines.append(f"\n### {category}")
            lines.append(f"**Story:** {example}")
            if ac:
                lines.append(f"**Sample AC:**\n{ac}")

    if metrics:
        lines.append(f"\n## Recommended Success Metrics")
        lines.append("| Metric | Category | Benchmark |")
        lines.append("|--------|----------|-----------|")
        for m in metrics:
            lines.append(f"| {m.get('Metric Name','')} | {m.get('Category','')} | {_truncate(m.get('Target Benchmark',''),60)} |")

    if antipatterns:
        lines.append(f"\n## Antipatterns to Avoid")
        for ap in antipatterns:
            name = ap.get("Antipattern Name", "")
            section = ap.get("Affects Section", "")
            fix = _truncate(ap.get("Fix", ""), 120)
            lines.append(f"\n**✗ {name}** _(section: {section})_")
            lines.append(f"Fix: {fix}")

    if oos:
        lines.append(f"\n## Common Out-of-Scope Mistakes")
        lines.append(f"> {oos}")

    if template_markdown:
        lines.append(f"\n## PRD Template Scaffold")
        lines.append("```markdown")
        lines.append(template_markdown[:2000])
        lines.append("```")

    return "\n".join(lines)


def persist_prd(prd_content: str, project_name: str, section: Optional[str], output_dir: Optional[str]) -> Tuple[str, Optional[str]]:
    """Save PRD scaffold to disk using the Master + Overrides pattern."""
    base = Path(output_dir) if output_dir else Path.cwd()
    project_slug = (project_name or "default").lower().replace(" ", "-")
    master_dir = base / "prd-docs" / project_slug

    master_dir.mkdir(parents=True, exist_ok=True)
    master_file = master_dir / "MASTER.md"
    master_file.write_text(prd_content, encoding="utf-8")

    if section:
        sections_dir = master_dir / "sections"
        sections_dir.mkdir(exist_ok=True)
        section_file = sections_dir / f"{section.lower().replace(' ', '-')}.md"
        section_file.write_text(
            f"# {section} — Section Override for {project_name}\n\n"
            f"> This file overrides MASTER.md for the {section} section.\n\n"
            f"[Fill in section-specific detail here]\n",
            encoding="utf-8"
        )
        return str(master_file), str(section_file)

    return str(master_file), None
