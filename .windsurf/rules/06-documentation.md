---
trigger: glob
globs: "docs/**/*.md,*.md"
---

# Documentation Conventions

## MkDocs Material
- Site config in mkdocs.yml at project root
- All docs under docs/ directory
- Use Mermaid for diagrams (via pymdownx.superfences)
- Use admonitions for warnings, tips, notes
- Code blocks with language annotation and copy button

## Markdown Style
- Use ATX headers (# not underlines)
- Tables for structured comparisons
- GIFs displayed via HTML `<img>` tags with width control for quality
- Relative paths for internal links
- No trailing whitespace

## ADR Format (docs/decisions/)
- Filename: NNN-short-description.md (e.g., 001-cpu-only-hpa.md)
- Sections: Status, Context, Decision, Consequences, Alternatives Considered
- Include measured data and trade-offs — not just opinions
- Link ADRs from relevant code and other docs

## Content Guidelines
- Write for a technical reviewer with 10+ years experience
- Lead with the "so what" — why does this decision matter?
- Include evidence: metrics, benchmarks, cost comparisons
- Be honest about limitations and trade-offs
