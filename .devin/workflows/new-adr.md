---
description: Create a new Architecture Decision Record with proper structure and numbering
---

# /new-adr Workflow

## 1. Determine ADR Number

```bash
ls docs/decisions/ | sort -n | tail -1
```
// turbo

Next number = last + 1, zero-padded to 3 digits.

## 2. Create ADR File

Use template at `templates/docs/decisions/adr-template.md`:

```bash
export ADR_NUM="NNN"
export ADR_SLUG="short-decision-name"
cp templates/docs/decisions/adr-template.md docs/decisions/${ADR_NUM}-${ADR_SLUG}.md
```

## 3. Fill in Sections

Required sections:
1. **Title**: `ADR-${ADR_NUM}: ${TITLE}`
2. **Status**: Proposed (will change to Accepted after review)
3. **Date**: Today's date (YYYY-MM-DD)
4. **Context**: What problem are we solving? What constraints exist?
5. **Options Considered**: Table with at least 2 options, Pros/Cons each
6. **Decision**: What we decided
7. **Rationale**: Why this option over alternatives
8. **Consequences**: Positive (what we gain) and Negative (what we trade off)
9. **Revisit When**: Conditions that would invalidate this decision

## 4. Validation Checklist

- [ ] Context explains the problem clearly for someone unfamiliar
- [ ] At least 2 options considered with honest pros/cons
- [ ] Decision is clear and actionable
- [ ] Rationale explains WHY, not just WHAT
- [ ] Consequences include both positive and negative
- [ ] Revisit When has concrete, measurable conditions
- [ ] Uses real measured data where applicable (not estimates)

## 5. Cross-Reference

- If the ADR relates to a specific service, reference it in the service README
- If the ADR introduces a new invariant, update `AGENTS.md`
- If the ADR changes a K8s pattern, update the relevant rule in `.windsurf/rules/`

## 6. Review

Request review from a peer or lead engineer. ADR moves from Proposed → Accepted after review.
