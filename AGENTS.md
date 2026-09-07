# Repository guidance for agents

## Purpose and scope

This project maintains a curated, multilingual directory of agent skills and MCP integrations useful to WordPress developers, plus a reproducible framework for comparing models with and without individual skills. It is a link catalog and benchmark, not an installable skill bundle or a production WordPress site.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing the catalog. For benchmark work, start with [benchmark/README.md](benchmark/README.md) and [benchmark/LANDING-PAGE.md](benchmark/LANDING-PAGE.md). Prefer the current code, configuration, and workflows when older prose disagrees, and update affected documentation with behavior changes.

## Repository map

| Path | Responsibility |
| --- | --- |
| `README.md` | English source edition of the catalog and project overview |
| `README.es.md`, `README.pt-BR.md` | Spanish and Brazilian Portuguese editions |
| `SOURCES.md` | Research provenance, verification scope, migrations, and exclusions |
| `scripts/validate_skills.py`, `tests/` | Catalog parity and upstream skill validation, with unit tests |
| `benchmark/__main__.py`, `core.py`, `runner.py` | CLI, task/configuration validation, execution, and resume logic |
| `benchmark/adapters/` | Provider API contracts, usage accounting, and model tools |
| `benchmark/project*.py`, `benchmark/environments/` | Project tooling, packaging, Playground runtime, browser checks, and evaluation |
| `benchmark/tasks/` | Public assignments, initial fixtures, hidden reference solutions, and acceptance criteria |
| `benchmark/configs/`, `benchmark/skills.lock.json` | Round definitions and pinned upstream skill resources |
| `benchmark/budget.py`, `ci_budget.py`, `budget-history.json` | Shared model budgets, CI history, and prior cost reservations |
| `benchmark/reporting.py`, `project_reporting.py`, `publish_results.py` | Reports, human review imports, and sanitized result publication |
| `benchmark/tests/` | Benchmark unit and simulated provider tests |
| `benchmark/results/` | Versioned, sanitized latest result snapshots per model |
| `results/`, `benchmark/.cache/` | Ignored raw runs, budget ledger, and downloaded resources |
| `.github/workflows/` | Catalog validation, simulated benchmark checks, and manually dispatched live runs |

Paths abbreviated within a table row are relative to that row's named directory.

## Catalog and localization rules

- Update all three READMEs together when changing their content. Preserve the same entries, skill names, URLs, commands, examples, and material limitations. Translate headings and adjust local table-of-contents anchors.
- Keep skill bullets inside the existing `skills:start` / `skills:end` comments, with the linked skill name first. MCP servers, adapters, plugins, and hosted integrations belong in their own tables.
- Inspect actual upstream `SKILL.md` instructions before adding a skill. Prefer maintainer-controlled sources and direct skill links; identify ownership, requirements, and beta or experimental status.
- Use concise descriptions with a concrete WordPress use case. Avoid unsupported claims, copied marketing text, and changing popularity counts.
- Record significant source changes, exclusions, migrations, and research limitations in `SOURCES.md`. Distinguish documentation review, fixture verification, and actual model runs; do not imply one proves another.
- Keep product names and identifiers unchanged in translations. Follow the Brazilian Portuguese glossary and translation guidance linked from `CONTRIBUTING.md`.
- The validator currently supports public GitHub skill sources. Extend it with regression tests for a new hosting provider instead of bypassing validation.

## Development and checks

Run commands from the repository root. Use Python 3.12+ and Node.js compatible with `package.json`; benchmark CI pins Python 3.12.10 and Node.js 22.16.0. The benchmark uses Python's standard library; catalog validation has separate dependencies in `scripts/requirements.txt`.

Catalog validation setup and checks:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_skills.py
npx markdownlint-cli2@0.23.2 '**/*.md' '.github/**/*.md'
lychee --config lychee.toml --no-progress '**/*.md' '.github/**/*.md'
git diff --check
```

Reuse an existing suitable virtual environment. Lychee must be installed separately; CI uses 0.24.2. The live source validator and external link checks require network access. An optional `GITHUB_TOKEN` increases GitHub API limits. Investigate rate limits and upstream outages instead of treating them as proof that a resource should be removed.

Benchmark setup and fast checks:

```sh
npm ci --ignore-scripts
python3 -m benchmark sync-skills
npm run benchmark:validate
npm run benchmark:test
python3 -m benchmark validate --config benchmark/configs/landing-page.json
```

`sync-skills` downloads and hash-verifies locked resources. Browser checks additionally need `npx playwright install chromium` (use `--with-deps` on Linux when system dependencies are needed). Playground may download runtime resources on first use.

Choose deeper checks according to the change:

| Change | Additional validation |
| --- | --- |
| Diagnostic fixtures or evaluators | `python3 -m benchmark verify-fixtures --category themes --output results/fixtures` (replace `themes` with the affected category; omit the flag for all categories) |
| Landing-page preview tools | `python3 -m benchmark verify-project-tools --output results/landing-tools` |
| Landing-page acceptance or fixtures | `python3 -m benchmark verify-project --output results/landing-audit` |
| Diagnostic execution or resume | `python3 -m benchmark run --config benchmark/configs/pilot.json --output results/pilot` |
| Project execution or resume | `python3 -m benchmark run --config benchmark/configs/landing-page-mock.json --output results/landing-mock` |

The last two commands use simulated models. For resume changes, repeat the identical command and verify completed executions are reused. Use a fresh output directory if protocol inputs changed. Documentation-only edits need formatting, relevant link checks, and whitespace checks; do not run full Playground audits for prose changes. Report checks actually run and any blockers.

## Benchmark integrity

- Keep diagnostic `files-only-v1` / `micro-v1` results separate from practical `wordpress-project-v2` / `landing-page-v1` results. The landing-page scenario measures a complete editable block theme; diagnostic tasks measure narrower contracts.
- Repository maintainers may inspect reference solutions and acceptance code. Evaluated models must never receive hidden reference source, final acceptance assertions, private review mappings, or raw manifests. Preserve the public/hidden boundary in prompts, tools, mounts, and exports.
- Keep model runs isolated, compare each model against its paired no-skill baseline, and apply only eligible skills. Do not give an evaluated model extra tools or ambient skills outside its declared profile.
- Preserve runtime and dependency pins. Review skill commits, resource URLs, individual hashes, and aggregate hashes together when updating `skills.lock.json`.
- When changing a task's contract or frozen materials, update its version and relevant fixtures. Verify the reference passes and deliberately broken variants fail the intended criteria; do not weaken checks merely to make a submission pass.
- Preserve original scores and evidence. Report supplemental audits separately from the original rubric. Keep artifact pass, execution completion, and delivery success distinct.
- Simulated runs validate the harness, not model quality. Missing telemetry is not zero, missing human reviews remain pending, and exploratory runs do not support broad rankings. Never invent human review scores.

## Live runs and artifacts

- Default to simulated validation for development. A paid run must be within the user's authorized scope and budget, use reviewed configuration, and pass an explicit `--live` flag. Inspect its `plan` before execution; do not assume every committed config is simulated.
- Preserve the shared `results/model-budget-ledger.json`, prior budget history, and unresolved reservations. Do not delete history, change `budget_group`, or start another directory to bypass an allowance. Reconcile history before moving execution hosts; do not run paid rounds simultaneously across hosts.
- Resume only an identical protocol in its existing output directory. Changed tasks, skills, code, lockfiles, or configuration require a new directory while retaining shared budget history. Do not automatically retry requests with uncertain billing.
- Read credentials from the process environment; the CLI does not auto-load `.env`. Never expose keys in output or pass provider credentials into WordPress/browser evaluation processes.
- Keep raw runs under ignored `results/`, fetched skills under `benchmark/.cache/`, and private configs in `benchmark/configs/*.local.json`. Do not commit `.env`, credentials, raw provider payloads, or hidden evaluation material through result exports.
- Use `python3 -m benchmark.publish_results --source results/ROUND --destination benchmark/results` for a reviewed round's public snapshot. Inspect the export before committing; publishing replaces that model's `latest` snapshot.

## Editing conventions

Check the working tree before editing and preserve unrelated changes. Keep changes focused on the requested task. Follow `.editorconfig`: UTF-8, LF, final newline, two-space indentation by default and four spaces for Python. Follow nearby code conventions rather than reformatting unrelated files.

Markdown lint intentionally allows long lines and compact tables. Keep catalog entries readable in diffs. Pin dependencies and GitHub Actions consistently with the existing project; update lockfiles when dependencies change. For behavior changes, add focused regression coverage in `tests/` or `benchmark/tests/` as appropriate and update the relevant guide.
