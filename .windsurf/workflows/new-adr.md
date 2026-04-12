---
description: Create a new Architecture Decision Record following the project ADR format
---

## New ADR Workflow

1. Ask the user for:
   - Short title for the decision (e.g., "CPU-only HPA for ML pods")
   - Context: What problem or question prompted this decision?

// turbo
2. Determine the next ADR number:
   ```bash
   ls docs/decisions/ | grep -E '^[0-9]+' | sort -n | tail -1
   ```

3. Create the ADR file at `docs/decisions/NNN-short-description.md` with this structure:

   ```markdown
   # ADR-NNN: <Title>

   ## Status
   Accepted | Proposed | Deprecated | Superseded by ADR-XXX

   ## Context
   What is the issue that we're seeing that is motivating this decision?
   Include metrics, incidents, or constraints that make this relevant.

   ## Decision
   What is the change that we're proposing and/or doing?
   Be specific — include configuration values, code patterns, tool choices.

   ## Consequences

   ### Positive
   - What becomes easier or better?

   ### Negative
   - What becomes harder or worse?
   - What trade-offs are we accepting?

   ### Neutral
   - What other effects does this have?

   ## Alternatives Considered
   | Alternative | Pros | Cons | Why Rejected |
   |-------------|------|------|-------------|
   | Option A | ... | ... | ... |
   | Option B | ... | ... | ... |

   ## References
   - Links to related ADRs, documentation, benchmarks
   ```

4. Update `docs/decisions/README.md` index table with the new ADR

5. If the ADR relates to code changes, add a reference comment or link in the relevant source files

6. Commit with message: `docs: add ADR-NNN <short-title>`
