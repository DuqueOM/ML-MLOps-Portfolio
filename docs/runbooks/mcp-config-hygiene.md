# Runbook — MCP config hygiene (D-17 / D-18)

Secure setup pattern for `~/.codeium/windsurf/mcp_config.json` and
equivalent agent configs. Applies to any MCP server that requires a
provider credential (GitHub PAT, cloud keys, API tokens).

## Principle

**Invariant D-17**: no literal credentials in any committed or
distributable config file. This applies equally to your local MCP
config even if it lives outside version control — a plaintext token
in a file has the same exposure surface as one in a git repo
(backup sync, screen shares, terminal history, session transcripts).

## Correct pattern

```json
{
  "mcpServers": {
    "github": {
      "serverUrl": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

Token lives in `~/.secrets.env` (chmod 600), sourced from `~/.zshrc`
or `~/.bashrc`:

```bash
# ~/.secrets.env — chmod 600 — never commit
export GITHUB_PERSONAL_ACCESS_TOKEN="github_pat_..."
```

```bash
# ~/.zshrc (or ~/.bashrc)
[ -f ~/.secrets.env ] && source ~/.secrets.env
```

## Anti-patterns

### Wrong: literal Authorization header

```json
{
  "github": {
    "headers": {
      "Authorization": "Bearer github_pat_11ABCD..."  // ❌ D-17 violation
    }
  }
}
```

### Wrong: literal in args

```json
{
  "supabase-mcp-server": {
    "args": ["-y", "@supabase/mcp-server-supabase", "--access-token", "sbp_abc123..."]  // ❌
  }
}
```

### Wrong: literal in env

```json
{
  "some-server": {
    "env": {
      "API_KEY": "sk-live-abc..."  // ❌ — use "${SOME_API_KEY}" instead
    }
  }
}
```

## Setup checklist (first time)

> **Bootstrap note (ADR-014 §5.3)**: `scripts/bootstrap.sh` is now PEP-668
> safe. It detects `uv` first, falls back to a project-local `.venv/`,
> and refuses to call bare `pip` against the system interpreter. If you
> prefer the fastest path: `curl -LsSf https://astral.sh/uv/install.sh | sh`
> before running bootstrap.

1. Create `~/.secrets.env` (chmod 600):
   ```bash
   touch ~/.secrets.env
   chmod 600 ~/.secrets.env
   ```
2. Add export lines per provider you use:
   ```bash
   # ~/.secrets.env
   export GITHUB_PERSONAL_ACCESS_TOKEN=""
   # export OTHER_API_KEY=""
   ```
3. Source from shell rc file:
   ```bash
   echo '[ -f ~/.secrets.env ] && source ~/.secrets.env' >> ~/.zshrc
   ```
4. Populate tokens by editing `~/.secrets.env` (keep chmod 600)
5. `source ~/.secrets.env` in your current shell
6. Restart your IDE / agent so the MCP subprocess inherits the env

## Validation

Before each Windsurf / Claude / Cursor session, run:

```bash
# Should return 0 hits — no literal credentials in your MCP config
grep -E 'github_pat_|pcsk_|sbp_|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{36}' \
  ~/.codeium/windsurf/mcp_config.json && echo "❌ LITERAL FOUND" || echo "✅ clean"
```

## If you find a literal

1. **STOP** — this is D-17. Use `/secret-breach` workflow.
2. Revoke the token at the provider immediately (don't rotate — revoke)
3. Generate a new one with least-privilege scopes
4. Follow the setup checklist above; never paste the new one back into
   the config file directly
5. Audit provider's security log for last 90 days
6. Delete any backup files that contained the literal
7. Document in `docs/incidents/YYYY-MM-DD-<slug>.md` (gitignored per
   template policy)

## Provider-specific tips

| Provider | Token prefix | Recommended scope | Rotation cadence |
|----------|--------------|-------------------|------------------|
| GitHub (fine-grained PAT) | `github_pat_` | `repo` + `read:org` (template default) | 90 days |
| GitHub (classic PAT) | `ghp_` | Avoid classic PATs — use fine-grained | — |
| Pinecone | `pcsk_` | Project-scoped | 180 days |
| Supabase | `sbp_` | Org-scoped only if needed | 90 days |
| AWS | `AKIA...` | Avoid access keys — use IRSA | N/A (no keys) |
| GCP | JSON SA key | Avoid — use Workload Identity | N/A (no keys) |

## Related

- Invariants D-17 (no hardcoded credentials), D-18 (cloud-native delegation)
- `.windsurf/skills/secret-breach-response/SKILL.md`
- `.windsurf/workflows/secret-breach.md`
- `docs/runbooks/secret-rotation.md` — scheduled rotation procedure
- `MEMORY[12-security-secrets.md]` — always-on security rule
