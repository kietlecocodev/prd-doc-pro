#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Doc Pro Exporter — convert PRD documents between formats.

Supports: markdown (default), confluence wiki, notion-ready, and clean text.
"""

import re
from pathlib import Path
from typing import Optional


def export_prd(content: str, output_format: str, output_path: Optional[str] = None) -> str:
    """Export PRD content to the specified format."""
    converters = {
        "markdown": _to_markdown,
        "confluence": _to_confluence,
        "notion": _to_notion,
        "text": _to_clean_text,
        "html": _to_html,
    }

    converter = converters.get(output_format)
    if not converter:
        return f"Error: Unknown format '{output_format}'. Available: {', '.join(converters.keys())}"

    result = converter(content)

    if output_path:
        Path(output_path).write_text(result, encoding="utf-8")

    return result


def _to_markdown(content: str) -> str:
    """Pass-through — content is already markdown."""
    return content


def _to_confluence(content: str) -> str:
    """Convert markdown to Confluence wiki markup."""
    lines = content.split("\n")
    output = []

    for line in lines:
        # Headers: # → h1., ## → h2., etc.
        header_match = re.match(r"^(#{1,6})\s+(.+)", line)
        if header_match:
            level = len(header_match.group(1))
            output.append(f"h{level}. {header_match.group(2)}")
            continue

        # Bold: **text** → *text*
        line = re.sub(r"\*\*(.+?)\*\*", r"*\1*", line)

        # Italic: _text_ → _text_ (same in Confluence)

        # Inline code: `text` → {{text}}
        line = re.sub(r"`([^`]+)`", r"{{\1}}", line)

        # Code blocks: ```lang → {code:lang}
        if line.strip().startswith("```"):
            lang = line.strip().replace("```", "").strip()
            if lang:
                output.append(f"{{code:language={lang}}}")
            else:
                # Closing code block
                output.append("{code}")
            continue

        # Checkbox: - [ ] → (/) unchecked, - [x] → (/) checked
        line = re.sub(r"^(\s*)- \[x\]\s*", r"\1(/) ", line)
        line = re.sub(r"^(\s*)- \[ \]\s*", r"\1(x) ", line)

        # Bullet list: - item → * item
        line = re.sub(r"^(\s*)- ", r"\1* ", line)

        # Numbered list: 1. item → # item
        line = re.sub(r"^(\s*)\d+\.\s+", r"\1# ", line)

        # Links: [text](url) → [text|url]
        line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[\1|\2]", line)

        # Tables: | a | b | → || a || b || for headers, | a | b | for data
        # Simple approach: pass through as-is (Confluence table syntax is similar)

        # Blockquote: > text → {quote}text{quote}
        quote_match = re.match(r"^>\s*(.+)", line)
        if quote_match:
            output.append(f"{{quote}}{quote_match.group(1)}{{quote}}")
            continue

        # Horizontal rule: --- → ----
        if re.match(r"^-{3,}$", line.strip()):
            output.append("----")
            continue

        output.append(line)

    return "\n".join(output)


def _to_notion(content: str) -> str:
    """Clean markdown optimized for Notion paste (Notion supports standard markdown)."""
    lines = content.split("\n")
    output = []

    for line in lines:
        # Notion handles standard markdown well, but some adjustments help:

        # Convert checkbox format
        line = re.sub(r"^(\s*)- \[x\]", r"\1- [x]", line)  # Notion uses same format
        line = re.sub(r"^(\s*)- \[ \]", r"\1- [ ]", line)

        # Ensure tables have proper spacing
        if "|" in line and re.match(r"^\|", line.strip()):
            # Clean up table alignment
            cells = line.split("|")
            cells = [c.strip() for c in cells]
            line = " | ".join(cells)
            if line.startswith(" | "):
                line = "|" + line[2:]
            if line.endswith(" | "):
                line = line[:-2] + "|"

        output.append(line)

    # Add Notion metadata header
    header = "---\n# Paste this into Notion — all formatting will be preserved\n---\n\n"
    return header + "\n".join(output)


def _to_clean_text(content: str) -> str:
    """Strip all markdown formatting for plain text output."""
    text = content

    # Remove headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)

    # Remove inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Remove links, keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)

    # Remove table separators
    text = re.sub(r"^\|[-| :]+\|$", "", text, flags=re.MULTILINE)

    # Clean up table pipes
    text = re.sub(r"\|", " | ", text)

    # Remove blockquote markers
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r"^-{3,}$", "=" * 60, text, flags=re.MULTILINE)

    # Remove checkboxes
    text = re.sub(r"- \[[ x]\]\s*", "- ", text)

    # Clean up multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _to_html(content: str) -> str:
    """Convert markdown to basic HTML for email or web sharing."""
    lines = content.split("\n")
    output = ["<!DOCTYPE html>", "<html>", "<head>",
              '<meta charset="utf-8">',
              '<style>',
              'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; '
              'max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333; }',
              'h1, h2, h3 { color: #1a1a1a; border-bottom: 1px solid #eee; padding-bottom: 8px; }',
              'table { border-collapse: collapse; width: 100%; margin: 16px 0; }',
              'th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }',
              'th { background: #f5f5f5; font-weight: 600; }',
              'code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }',
              'pre { background: #f4f4f4; padding: 16px; border-radius: 4px; overflow-x: auto; }',
              'blockquote { border-left: 4px solid #ddd; margin: 16px 0; padding: 8px 16px; color: #666; }',
              '.checklist { list-style: none; padding-left: 0; }',
              '.checklist li::before { content: "☐ "; }',
              '.checklist li.checked::before { content: "☑ "; }',
              '</style>',
              "</head>", "<body>"]

    in_code_block = False
    in_table = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                output.append("</code></pre>")
                in_code_block = False
            else:
                lang = line.strip().replace("```", "").strip()
                output.append(f"<pre><code class='{lang}'>")
                in_code_block = True
            continue

        if in_code_block:
            output.append(_html_escape(line))
            continue

        # Headers
        header_match = re.match(r"^(#{1,6})\s+(.+)", line)
        if header_match:
            level = len(header_match.group(1))
            text = _inline_md_to_html(header_match.group(2))
            output.append(f"<h{level}>{text}</h{level}>")
            continue

        # Table
        if "|" in line and re.match(r"^\s*\|", line.strip()):
            if re.match(r"^\s*\|[-| :]+\|\s*$", line):
                continue  # Skip separator row
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                output.append("<table>")
                tag = "th"
                in_table = True
            else:
                tag = "td"
            row = "".join(f"<{tag}>{_inline_md_to_html(c)}</{tag}>" for c in cells)
            output.append(f"<tr>{row}</tr>")
            continue
        elif in_table:
            output.append("</table>")
            in_table = False

        # Horizontal rule
        if re.match(r"^-{3,}$", line.strip()):
            output.append("<hr>")
            continue

        # Blockquote
        quote_match = re.match(r"^>\s*(.+)", line)
        if quote_match:
            output.append(f"<blockquote>{_inline_md_to_html(quote_match.group(1))}</blockquote>")
            continue

        # Checkbox list
        checkbox_match = re.match(r"^(\s*)- \[([ x])\]\s*(.+)", line)
        if checkbox_match:
            checked = 'checked' if checkbox_match.group(2) == 'x' else ''
            text = _inline_md_to_html(checkbox_match.group(3))
            output.append(f'<div><input type="checkbox" {checked} disabled> {text}</div>')
            continue

        # Bullet list
        bullet_match = re.match(r"^(\s*)[-*]\s+(.+)", line)
        if bullet_match:
            text = _inline_md_to_html(bullet_match.group(2))
            output.append(f"<li>{text}</li>")
            continue

        # Numbered list
        num_match = re.match(r"^(\s*)\d+\.\s+(.+)", line)
        if num_match:
            text = _inline_md_to_html(num_match.group(2))
            output.append(f"<li>{text}</li>")
            continue

        # Empty line
        if not line.strip():
            output.append("<br>")
            continue

        # Paragraph
        output.append(f"<p>{_inline_md_to_html(line)}</p>")

    if in_table:
        output.append("</table>")

    output.extend(["</body>", "</html>"])
    return "\n".join(output)


def _html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _inline_md_to_html(text: str) -> str:
    text = _html_escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text
