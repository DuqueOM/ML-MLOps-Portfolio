<div class="portfolio-page" markdown="1">

# ADR-019: One uv Workspace and One Lock for Every Environment

- **Status**: Accepted
- **Date**: 2026-10-28
- **Authors**: Duque Ortega Mutis
- **Relates to**: [ADR-005](005-compatible-release-pinning.md) (kept: `~=` stays the
  declaration rule; this record fulfils its "Revisit When — adopting a lockfile")

> **TL;DR**: The three services and `common_utils` become one
> [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) with a
> single `uv.lock`, on Python 3.13 only. Local development, every CI job and
> every image install from that lock with `uv sync --frozen`, so the versions a
> model is trained with, tested with and served with are the same versions —
> by construction, not by discipline.

---

## Context

Each service declared its dependencies in up to four places — `requirements.in`,
a hashed `requirements.txt`, `requirements-prod.txt` and `pyproject.toml` — and
no consumer read all of them. Each consumer read a different one:

| Consumer | Read | Effect, measured on `main` (a73c769) |
| --- | --- | --- |
| BankChurn image | `requirements-prod.txt` + an inline `xgboost>=1.5,<3.0` | Served with xgboost **2.x** a model trained with xgboost **3.x** |
| BankChurn training | `requirements.in` (unlocked) | Resolved scikit-learn **1.9**, newer than the **1.8** the image served with — the direction ADR-005's amendment forbids |
| Published artifacts | — | Saved with scikit-learn **1.7.2**: neither of the two |
| CI tests | `requirements.in`, or a hash-stripped lock, + unpinned test tools | Tested Python 3.11 / 3.12; the images run 3.13 (ChicagoTaxi ran 3.11) |
| CI integration models | inline `scikit-learn~=1.6.0 numpy~=1.26.0` | Integration tests exercised a third stack |
| pip-audit | the runner's interpreter | Audited bandit and pip-audit — none of the services' packages |
| ChicagoTaxi ETL | an **untracked**, unpinned `requirements.txt` | PySpark and Dask were not declared anywhere in the repository |

ADR-005's `~=` was applied in each file, and every file drifted from the
others anyway. A pin rule constrains one declaration; nothing made the
declarations agree.

---

## Decision

1. **One workspace, one lock.** The root `pyproject.toml` is a virtual project
   (`[tool.uv] package = false`) whose `[tool.uv.workspace]` lists the three
   services and `common_utils`. `uv lock` resolves all of them together into
   one `uv.lock`; a package used by two services has **one** version.
2. **One declaration per service.** A service's `pyproject.toml`
   `dependencies` is exactly what its image installs and its code imports.
   Everything else is a `[dependency-groups]` group: `train` (mlflow, optuna,
   evidently, …), `notebook`, and ChicagoTaxi's `etl` (PySpark, Dask). Dev tools
   (pytest, black, flake8, isort, mypy, httpx) are the root `dev` group. The
   `requirements*.txt/.in` files are deleted. `~=` (ADR-005) remains the rule
   for every entry.
3. **One Python.** `requires-python = ">=3.13,<3.14"`, `.python-version` = `3.13`,
   the CI matrix is `['3.13']` and all three images are
   `python:3.13.15-slim-bookworm`.
4. **The published models' versions win.** Where the lock could choose, it was
   pinned to what the committed artifacts were saved with: `scikit-learn ~= 1.7.2`,
   `joblib ~= 1.6.0`. All five published artifacts load under the lock with no
   `InconsistentVersionWarning`.
5. **Images install from the lock.** Build context is the repository root
   (`docker build -f <service>/Dockerfile .`). The builder copies `uv` (pinned,
   `ghcr.io/astral-sh/uv:0.11.19`), the root `pyproject.toml`, `uv.lock` and the
   member manifests, then runs
   `uv sync --frozen --no-dev --package <service> --no-install-workspace`.
   `<service>/Dockerfile.dockerignore` is a whitelist, so the root context
   sends only what that service needs.
6. **CPU-only ML wheels.** `torch` resolves from the PyTorch CPU index (an
   *explicit* index, used for torch alone); BankChurn depends on `xgboost-cpu`.
   No `nvidia-*` package is in any image.
7. **CI installs from the lock and checks it.** Every job uses
   `astral-sh/setup-uv` + `uv sync --frozen`. `--frozen` trusts the lock, so the
   Quality Gates job runs `uv lock --check`: a `pyproject.toml` changed without
   re-locking fails the PR. pip-audit audits `uv export` of the whole lock.
   The `uv-lock` pre-commit hook re-locks on commit.
8. **Dependabot watches the lock** with the `uv` ecosystem; `pip` keeps only
   `requirements-docs.txt` and `requirements-dvc.txt`, which are tools outside
   the workspace (`uvx` runs DVC in its own environment).

### Verification (this change, before merge)

| Check | BankChurn | ChicagoTaxi | NLPInsight |
| --- | --- | --- | --- |
| Tests from the lock | 198 passed, cov 90.12 % | 122 passed, cov 99.03 % | 73 passed (+1 xpassed), cov 98.41 % |
| flake8 / black / isort | clean | clean | clean |
| Image build from `uv.lock` | OK | OK | OK (incl. the torch curl fallback, sha256-verified against the lock) |
| In the image | 3.13.15, sklearn 1.7.2, numpy 2.4.6 | same | same |
| `nvidia-*` / dev tools in the image | none | none | none |
| Published model loads in the container | `Pipeline` | `RandomForestRegressor` | `Pipeline` |
| `GET /health` | `healthy` | `degraded`¹ | `healthy` |

¹ Same as `main`: the precomputed predictions live in `data/`, which the image
has never contained; they are mounted at runtime.

---

## Alternatives Considered

| Option | Verdict |
| --- | --- |
| Keep pip-tools (`requirements.in` → `pip-compile`) | Rejected — it was already the documented process and the table above is its result: nothing forced the other consumers to read the compiled file |
| One lock **per service** (three uv projects) | Rejected — shared packages (numpy, pandas, sklearn, fastapi, `common_utils`) could again diverge between services, and three locks need three Dependabot streams and three audits |
| Poetry | Rejected — no native workspaces, so one lock across the services is not available |
| Conda environment files | Rejected — not what the images install, and no cross-platform lock with hashes |
| Support Python 3.11–3.13 | Rejected — xgboost 3.4 requires ≥ 3.12 and pyarrow 17 has no 3.13 wheel; a matrix of Pythons nothing runs in production tests a combination that is never deployed |

---

## Consequences

- **Positive**: Train = test = serve. A version can no longer differ between
  the environment that produces an artifact and the one that loads it.
- **Positive**: Exact versions **and hashes** for every package, every
  platform, in one reviewed file; images and CI fail rather than re-resolve.
- **Positive**: Security scanning and Dependabot see the real dependency set,
  including transitive packages.
- **Positive**: The ChicagoTaxi ETL is reproducible from a clone for the
  first time (`make install`).
- **Negative**: One-version rule — a service's upgrade can be blocked by
  another's constraint (today: `pyarrow ~= 25.0.1`, because mlflow 3.16 in
  BankChurn's `train` group requires `< 26`, also caps ChicagoTaxi).
- **Negative**: Every `docker build` now uses the repository root as context
  (workflows, compose files and Makefiles were changed accordingly); a build
  from inside a service directory no longer works.
- **Negative**: uv becomes a required tool, and its version is pinned in three
  kinds of places (`UV_VERSION` in workflows, `setup-uv`, the Dockerfiles'
  `COPY --from`). They move together, in one PR.
- **Negative**: Python 3.14 waits until every locked package publishes 3.14
  wheels — a portfolio-wide decision, not an image bump.

## Revisit When

- Two services need versions of a package that cannot coexist — first try
  `[tool.uv] conflicts`; split that service out of the workspace only if that fails.
- Python 3.14 wheels exist for the whole lock (torch, xgboost, lightgbm, pyarrow, shap).
- Dependabot's `uv` ecosystem proves unable to update workspace members (the
  `uv lock --check` gate makes that visible as failing PRs, not as drift).

---

## References

- [uv — Workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [uv — Using uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/)
- [uv — Locking and syncing (`--frozen`, `--locked`)](https://docs.astral.sh/uv/concepts/projects/sync/)
- [ADR-005 — Compatible Release Pinning](005-compatible-release-pinning.md)

</div>
