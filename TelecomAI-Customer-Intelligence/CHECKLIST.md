# Acceptance Checklist

Before merging any changes to `main`, verify the following:

## 1. Code Quality
- [ ] **Linting:** No errors from `ruff` or `flake8`.
- [ ] **Types:** `mypy` passes without errors (strict mode where possible).
- [ ] **Format:** Code is formatted with `black` and imports sorted with `isort`.

## 2. Testing
- [ ] **Unit Tests:** All tests in `tests/` pass (`pytest`).
- [ ] **Coverage:** Test coverage is at least 75%.
- [ ] **Integration:** `test_api_e2e.py` passes (verifying Docker/API logic).
- [ ] **Logic:** `test_model_logic.py` confirms model determinism on synthetic data.

## 3. Reproducibility
- [ ] **Dependencies:** `requirements.txt` is up-to-date and pinned.
- [ ] **Docker:** The image builds successfully (`docker build .`).
- [ ] **One-Click Demo:** `make docker-demo` brings up a working API.

## 4. Documentation
- [ ] **README:** Updated with any new features or commands.
- [ ] **Docs:** New files in `src/` have corresponding entries in `docs/_per_file/` if critical.
- [ ] **Architecture:** `ARCHITECTURE.md` reflects current system design.
