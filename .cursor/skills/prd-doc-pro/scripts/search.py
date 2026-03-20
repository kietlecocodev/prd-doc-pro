#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Doc Pro Search — CLI entry point for PRD knowledge base queries.

Usage:
  python3 scripts/search.py "<query>" --generate-prd [-p "Project Name"]
  python3 scripts/search.py "<query>" --domain <domain> [-n <max_results>]
  python3 scripts/search.py "<query>" --generate-prd --persist [-p "Project Name"] [--section "requirements"]

Domains: product-type, section, user-story, antipattern, metric, template
"""

import argparse
import sys
import io

from core import AVAILABLE_DOMAINS, MAX_RESULTS, search, search_domain
from generator import generate_prd, persist_prd

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def format_output(result: dict) -> str:
    if "error" in result:
        return f"Error: {result['error']}"

    lines = [
        "## PRD Doc Pro Search Results",
        f"**Domain:** {result.get('domain', 'all')} | **Query:** {result['query']}",
        f"**Found:** {result['count']} result(s)\n",
    ]

    for i, row in enumerate(result["results"], 1):
        lines.append(f"### Result {i}")
        for key, value in row.items():
            v = str(value)
            if len(v) > 350:
                v = v[:350] + "..."
            lines.append(f"- **{key}:** {v}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PRD Doc Pro Search")
    parser.add_argument("query", help="Search query (describe the product, feature, or topic)")
    parser.add_argument("--domain", "-d", choices=AVAILABLE_DOMAINS,
                        help="Search a specific knowledge domain")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS,
                        help=f"Max results to return (default: {MAX_RESULTS})")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # PRD generation
    parser.add_argument("--generate-prd", "-g", action="store_true",
                        help="Generate a complete PRD scaffold for the described product/feature")
    parser.add_argument("--project-name", "-p", type=str, default=None,
                        help="Project name (used in the generated PRD header)")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii",
                        help="Output format for generated PRD (default: ascii)")

    # Persistence (Master + Overrides pattern, mirrors ui-ux-pro-max)
    parser.add_argument("--persist", action="store_true",
                        help="Save generated PRD to prd-docs/<project>/MASTER.md")
    parser.add_argument("--section", type=str, default=None,
                        help="Also create a section-specific override file in prd-docs/<project>/sections/")
    parser.add_argument("--output-dir", "-o", type=str, default=None,
                        help="Directory to save persisted files (default: current directory)")

    args = parser.parse_args()

    # ── Generate full PRD scaffold ──────────────────────────────────────
    if args.generate_prd:
        result = generate_prd(
            args.query,
            project_name=args.project_name,
            output_format=args.format,
            persist=args.persist,
            section=args.section,
            output_dir=args.output_dir,
        )
        print(result)

        if args.persist:
            prd_content = generate_prd(
                args.query,
                project_name=args.project_name,
                output_format="markdown",
            )
            master_path, section_path = persist_prd(
                prd_content,
                project_name=args.project_name or "default",
                section=args.section,
                output_dir=args.output_dir,
            )
            slug = (args.project_name or "default").lower().replace(" ", "-")
            print("\n" + "=" * 60)
            print(f"✅ PRD persisted to prd-docs/{slug}/")
            print(f"   📄 {master_path}  (Master PRD)")
            if section_path:
                print(f"   📄 {section_path}  (Section override)")
            print()
            print(f"📖 Usage: When working on a specific section, check")
            print(f"   prd-docs/{slug}/sections/<section>.md first.")
            print(f"   If it exists, its rules override MASTER.md.")
            print("=" * 60)

    # ── Domain search ───────────────────────────────────────────────────
    else:
        result = search(args.query, domain=args.domain, max_results=args.max_results)
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_output(result))
