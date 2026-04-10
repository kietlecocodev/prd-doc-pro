#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Doc Pro Search — CLI entry point for PRD knowledge base queries.

Usage:
  python3 scripts/search.py "<query>" --generate-prd [-p "Project Name"]
  python3 scripts/search.py "<query>" --domain <domain> [-n <max_results>]
  python3 scripts/search.py --review <file> [--strict] [--fix]
  python3 scripts/search.py "<query>" --generate-prd --persist [-p "Project Name"] [--section "requirements"]

Domains: product-type, section, user-story, antipattern, metric, template
"""

import argparse
import sys
import io

from core import AVAILABLE_DOMAINS, MAX_RESULTS, search, search_domain
from generator import generate_prd, persist_prd
from reviewer import review_prd, render_scorecard
from exporter import export_prd

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
    parser.add_argument("query", nargs="?", default=None,
                        help="Search query (describe the product, feature, or topic)")
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

    # PRD review
    parser.add_argument("--review", "-r", type=str, default=None, metavar="FILE",
                        help="Review a PRD file and produce a quality scorecard")
    parser.add_argument("--strict", action="store_true",
                        help="Strict review mode — penalizes missing optional sections")
    parser.add_argument("--fix", action="store_true",
                        help="After review, output an improved version with fixes applied")
    parser.add_argument("--mobile", action="store_true",
                        help="Force mobile product context (auto-detected by default)")

    # Persistence (Master + Overrides pattern)
    parser.add_argument("--persist", action="store_true",
                        help="Save generated PRD to prd-docs/<project>/MASTER.md")
    parser.add_argument("--section", type=str, default=None,
                        help="Also create a section-specific override file in prd-docs/<project>/sections/")
    parser.add_argument("--output-dir", "-o", type=str, default=None,
                        help="Directory to save persisted files (default: current directory)")

    # Platform targeting
    parser.add_argument("--platform", type=str, default=None,
                        help="Target platform(s): ios, android, or ios,android")

    # Export
    parser.add_argument("--export", type=str, default=None, metavar="FILE",
                        help="Export a PRD file to another format")
    parser.add_argument("--export-format", choices=["markdown", "confluence", "notion", "text", "html"],
                        default="markdown", help="Target format for export")
    parser.add_argument("--export-output", type=str, default=None, metavar="OUTPUT",
                        help="Output file path for export (default: stdout)")

    # Examples
    parser.add_argument("--example", "-e", type=str, default=None, metavar="NAME",
                        help="Show a gold-standard PRD example. E.g.: good/01-problem-statement, bad/02-user-stories")
    parser.add_argument("--list-examples", action="store_true",
                        help="List all available PRD examples")

    args = parser.parse_args()

    # ── Export a PRD file ────────────────────────────────────────────────
    if args.export:
        from pathlib import Path
        p = Path(args.export)
        if not p.exists():
            print(f"Error: File not found: {args.export}", file=sys.stderr)
            sys.exit(1)
        prd_text = p.read_text(encoding="utf-8")
        result = export_prd(prd_text, args.export_format, args.export_output)
        if args.export_output:
            print(f"Exported to {args.export_output} ({args.export_format} format)")
        else:
            print(result)
        sys.exit(0)

    # ── List or show examples ──────────────────────────────────────────
    if args.list_examples:
        from pathlib import Path
        examples_dir = Path(__file__).parent.parent / "data" / "details" / "examples"
        index_file = examples_dir / "INDEX.md"
        if index_file.exists():
            print(index_file.read_text(encoding="utf-8"))
        else:
            print("No examples index found.")
        sys.exit(0)

    if args.example:
        from pathlib import Path
        examples_dir = Path(__file__).parent.parent / "data" / "details" / "examples"
        name = args.example
        if not name.endswith(".md"):
            name += ".md"
        example_file = examples_dir / name
        if example_file.exists():
            print(example_file.read_text(encoding="utf-8"))
        else:
            print(f"Example not found: {name}", file=sys.stderr)
            print(f"Available examples:", file=sys.stderr)
            for f in sorted(examples_dir.rglob("*.md")):
                if f.name != "INDEX.md":
                    rel = f.relative_to(examples_dir)
                    print(f"  --example {str(rel).replace('.md', '')}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # ── Review an existing PRD ─────────────────────────────────────────
    if args.review:
        review_path = args.review
        if review_path == "-":
            prd_text = sys.stdin.read()
        else:
            from pathlib import Path
            p = Path(review_path)
            if not p.exists():
                print(f"Error: File not found: {review_path}", file=sys.stderr)
                sys.exit(1)
            prd_text = p.read_text(encoding="utf-8")

        result = review_prd(prd_text, strict=args.strict, is_mobile=args.mobile)

        if args.json:
            import json
            # Remove lambda-containing fields for JSON serialization
            serializable = {k: v for k, v in result.items()}
            print(json.dumps(serializable, indent=2, ensure_ascii=False, default=str))
        else:
            print(render_scorecard(result, output_format=args.format))

        sys.exit(0 if result["score"] >= 60 else 1)

    # ── Generate full PRD scaffold ──────────────────────────────────────
    if args.generate_prd:
        if not args.query:
            print("Error: query is required for --generate-prd", file=sys.stderr)
            sys.exit(1)

        platforms = args.platform.split(",") if args.platform else None
        result = generate_prd(
            args.query,
            project_name=args.project_name,
            output_format=args.format,
            persist=args.persist,
            section=args.section,
            output_dir=args.output_dir,
            platforms=platforms,
        )
        print(result)

        if args.persist:
            prd_content = generate_prd(
                args.query,
                project_name=args.project_name,
                output_format="markdown",
                platforms=platforms,
            )
            master_path, section_path = persist_prd(
                prd_content,
                project_name=args.project_name or "default",
                section=args.section,
                output_dir=args.output_dir,
            )
            slug = (args.project_name or "default").lower().replace(" ", "-")
            print("\n" + "=" * 60)
            print(f"PRD persisted to prd-docs/{slug}/")
            print(f"   {master_path}  (Master PRD)")
            if section_path:
                print(f"   {section_path}  (Section override)")
            print()
            print(f"Usage: When working on a specific section, check")
            print(f"   prd-docs/{slug}/sections/<section>.md first.")
            print(f"   If it exists, its rules override MASTER.md.")
            print("=" * 60)

    # ── Domain search ───────────────────────────────────────────────────
    else:
        if not args.query:
            print("Error: query is required for domain search", file=sys.stderr)
            sys.exit(1)

        result = search(args.query, domain=args.domain, max_results=args.max_results)
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_output(result))
