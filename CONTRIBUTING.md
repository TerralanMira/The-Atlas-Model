# Contributing to The Atlas Model

> **Principle:** Small, reviewable changes; clear intent; evidence where possible.

## 1) Flow
- Fork + branch from `main`: `type/short-topic` (e.g., `feat/observer-collapse`).
- Open an Issue first. Every PR must reference an Issue (`Fixes #123`).
- Prefer multiple small PRs over one giant one.

## 2) Issues (source of truth)
Use the templates. Tag each issue with:
- **Type:** `type:feature` | `type:story` | `type:bug` | `type:research`
- **Stage:** `stage:speculation` | `stage:theory` | `stage:testable` | `stage:implemented`
- **Area:** `area:ethics` `area:observation` `area:harmonics` `area:sims` etc.
- **Signals (optional):** `signal:math` `signal:empirical` `signal:design` `signal:docs`

## 3) Commits
- Conventional style: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Scope optional: `feat(sim): add standing-wave lattice`.

## 4) Pull Requests
- Keep to 300–600 lines of diff when possible.
- Include: **Problem**, **Intent**, **Changes**, **Evidence**, **Notes**.
- Link ADR if architectural: `docs/ADR/NNNN-title.md`.

### PR Checklist
- [ ] Linked issue(s) and labels applied
- [ ] Tests added/updated; `pytest` passes
- [ ] Lint/format pass (`ruff`/`black`), type-check (`mypy`) if applicable
- [ ] Docs updated (user + dev) and examples runnable
- [ ] Built docs locally: `mkdocs build` (also runs in CI)
- [ ] No breaking changes, or BREAKING CHANGE explained

## 5) Decision Records (ADR)
- Create an ADR for any non-trivial design or terminology choice.
- Template: `docs/ADR/0000-template.md`
- Status: `Proposed` → `Accepted` → `Superseded`.

## 6) Code Style
- Python: `ruff` + `black`, `mypy --strict` for packages
- Notebooks: keep outputs cleared; put reusable code in modules.
- Data: include small fixtures only; large data via pointers or `data/README`.

## 7) Docs
- Built with **MkDocs** (Material). All math via `pymdownx.arithmatex`.
- Tag claims in docs as **speculation/theory/tested**.

## 8) Safety & Ethics
- Follow `CODE_OF_CONDUCT.md`. Flag sensitive content with `ethics:` notes.

## 9) Releasing
- Squash & merge to `main`; tags like `v0.1.0`.
- Update `CHANGELOG.md` (generated from conventional commits if configured).
