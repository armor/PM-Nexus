#!/usr/bin/env python3
"""
Markdown to Atlassian Document Format (ADF) converter.
Handles common markdown elements for JIRA descriptions.
"""
import re
from typing import List, Dict, Any

def markdown_to_adf(markdown: str) -> Dict[str, Any]:
    """Convert markdown text to Atlassian Document Format (ADF)."""
    lines = markdown.split('\n')
    content = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Code block (```)
        if line.strip().startswith('```'):
            code_lines = []
            language = line.strip()[3:] or 'text'
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            content.append({
                "type": "codeBlock",
                "attrs": {"language": language},
                "content": [{"type": "text", "text": '\n'.join(code_lines)}]
            })
            i += 1
            continue

        # Heading (# ## ###)
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = min(len(heading_match.group(1)), 6)
            text = heading_match.group(2).strip()
            content.append({
                "type": "heading",
                "attrs": {"level": level},
                "content": parse_inline(text)
            })
            i += 1
            continue

        # Horizontal rule (---)
        if re.match(r'^-{3,}$', line.strip()):
            content.append({"type": "rule"})
            i += 1
            continue

        # Table (| header | header |)
        if line.strip().startswith('|'):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                # Skip separator row (|---|---|)
                if re.match(r'^\|[\s\-:|]+\|$', row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.split('|')[1:-1]]
                is_header = len(table_rows) == 0
                row = {
                    "type": "tableRow",
                    "content": [
                        {
                            "type": "tableHeader" if is_header else "tableCell",
                            "content": [{"type": "paragraph", "content": parse_inline(cell)}]
                        }
                        for cell in cells
                    ]
                }
                table_rows.append(row)
                i += 1
            if table_rows:
                content.append({
                    "type": "table",
                    "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                    "content": table_rows
                })
            continue

        # Bullet list (- or *)
        if re.match(r'^[\-\*]\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^[\-\*]\s+', lines[i]):
                item_text = re.sub(r'^[\-\*]\s+', '', lines[i])
                list_items.append({
                    "type": "listItem",
                    "content": [{"type": "paragraph", "content": parse_inline(item_text)}]
                })
                i += 1
            content.append({
                "type": "bulletList",
                "content": list_items
            })
            continue

        # Numbered list (1. 2. etc)
        if re.match(r'^\d+\.\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                item_text = re.sub(r'^\d+\.\s+', '', lines[i])
                list_items.append({
                    "type": "listItem",
                    "content": [{"type": "paragraph", "content": parse_inline(item_text)}]
                })
                i += 1
            content.append({
                "type": "orderedList",
                "content": list_items
            })
            continue

        # Regular paragraph
        para_lines = [line]
        i += 1
        # Collect continuation lines (not special)
        while i < len(lines):
            next_line = lines[i]
            if (not next_line.strip() or
                next_line.strip().startswith('#') or
                next_line.strip().startswith('```') or
                next_line.strip().startswith('|') or
                next_line.strip().startswith('-') or
                next_line.strip().startswith('*') or
                re.match(r'^\d+\.\s+', next_line)):
                break
            para_lines.append(next_line)
            i += 1

        para_text = ' '.join(para_lines)
        content.append({
            "type": "paragraph",
            "content": parse_inline(para_text)
        })

    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def parse_inline(text: str) -> List[Dict[str, Any]]:
    """Parse inline markdown (bold, italic, code, links)."""
    if not text:
        return [{"type": "text", "text": ""}]

    result = []
    remaining = text

    while remaining:
        # Bold **text** or __text__
        bold_match = re.search(r'\*\*(.+?)\*\*|__(.+?)__', remaining)
        # Italic *text* or _text_ (but not ** or __)
        italic_match = re.search(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', remaining)
        # Inline code `text`
        code_match = re.search(r'`([^`]+)`', remaining)
        # Link [text](url)
        link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', remaining)

        # Find earliest match
        matches = []
        if bold_match:
            matches.append(('bold', bold_match))
        if italic_match:
            matches.append(('italic', italic_match))
        if code_match:
            matches.append(('code', code_match))
        if link_match:
            matches.append(('link', link_match))

        if not matches:
            # No more inline formatting
            if remaining:
                result.append({"type": "text", "text": remaining})
            break

        # Get earliest match
        matches.sort(key=lambda x: x[1].start())
        match_type, match = matches[0]

        # Add text before match
        if match.start() > 0:
            result.append({"type": "text", "text": remaining[:match.start()]})

        # Add formatted text
        if match_type == 'bold':
            inner = match.group(1) or match.group(2)
            result.append({
                "type": "text",
                "text": inner,
                "marks": [{"type": "strong"}]
            })
        elif match_type == 'italic':
            inner = match.group(1) or match.group(2)
            result.append({
                "type": "text",
                "text": inner,
                "marks": [{"type": "em"}]
            })
        elif match_type == 'code':
            result.append({
                "type": "text",
                "text": match.group(1),
                "marks": [{"type": "code"}]
            })
        elif match_type == 'link':
            result.append({
                "type": "text",
                "text": match.group(1),
                "marks": [{"type": "link", "attrs": {"href": match.group(2)}}]
            })

        remaining = remaining[match.end():]

    return result if result else [{"type": "text", "text": ""}]


if __name__ == "__main__":
    # Test
    test_md = """# Heading 1

This is a **bold** paragraph with `inline code`.

## Heading 2

- Item 1
- Item 2

| Col1 | Col2 |
|------|------|
| A | B |

```rust
fn main() {
    println!("Hello");
}
```
"""
    import json
    print(json.dumps(markdown_to_adf(test_md), indent=2))
