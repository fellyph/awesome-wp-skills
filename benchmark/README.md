# WordPress model and skill benchmark

A reproducible benchmark for [issue #4](https://github.com/fellyph/awesome-wp-skills/issues/4). It compares each model without a skill against that same model with one eligible skill. WordPress artifacts run in a fresh Playground instance; the model agent runs outside WordPress.

The implementation includes 15 focused tasks in five categories, six pinned skill sources, native provider adapters, an optional OpenRouter route, simulated CI runs, cost checkpoints and Markdown/JSON/CSV reports. **Bundled configurations use simulated models. Their results test the benchmark, not the quality of real models or skills.**

## Install and validate

Use Python 3.12+ and Node.js 22.16.0. CI pins Python 3.12.10 and Node.js 22.16.0 on Ubuntu 24.04. No Python packages are required by the benchmark itself.

```sh
npm ci --ignore-scripts
npx playwright install chromium
python3 -m benchmark sync-skills
python3 -m benchmark validate
python3 -m unittest discover -s benchmark/tests -v
python3 -m benchmark verify-fixtures --output results/fixtures
```

On Linux CI, install Chromium system dependencies with `npx playwright install --with-deps chromium`. Playground downloads its WordPress/PHP resources on first use. WordPress 6.9, PHP 8.3, Playground 3.1.52, Playwright 1.63.0 and axe 4.13.0 are fixed in the Blueprints and npm lockfile. The PHP patch/build is the one bundled with the locked runtime.

`sync-skills` downloads only the resources listed in [skills.lock.json](skills.lock.json), verifies every file hash, and keeps them in an ignored cache. Revisions are immutable upstream commits. Existing local `benchmark/skills/` experiments are not read or modified by the runner. To change a skill, explicitly review and update the lock's commit, resource URLs, individual hashes and aggregate hash together.

## Run the simulated pilot

```sh
python3 -m benchmark plan --config benchmark/configs/pilot.json
python3 -m benchmark run --config benchmark/configs/pilot.json --output results/pilot
python3 -m benchmark report results/pilot
```

The pilot has two correction tasks, two simulated model behaviors, no skill or one of two eligible skills, and three repetitions: **36 executions**. The reference mock copies a known correct solution; the initial mock leaves the faulty project unchanged. Neither calls an API or pretends to reason with a skill.

[smoke.json](configs/smoke.json) exercises all five categories in 26 runs. [full.json](configs/full.json) expands to all 15 tasks. `plan` prints the exact matrix before execution. Commands must run from the repository root.

## Native APIs and OpenRouter

Every adapter exposes the same four tools: list files, read a file, write a project file, and delete a project file. The selected `SKILL.md` is loaded into the initial prompt; its references can be read through the same file interface. All conversation state and project contents start fresh for each execution.

| Adapter | Model family | Credential environment variable | Wire API |
| --- | --- | --- | --- |
| `openai` | GPT models, including GPT-6 Astra | `OPENAI_API_KEY` | Responses |
| `anthropic` | Claude | `ANTHROPIC_API_KEY` | Messages |
| `kimi` | Kimi | `MOONSHOT_API_KEY` | Chat Completions |
| `glm` | GLM | `ZAI_API_KEY` | Chat Completions |
| `gemini` | Google Gemini | `GEMINI_API_KEY` | generateContent |
| `openrouter` | Any supported tool-capable model | `OPENROUTER_API_KEY` | Routed Chat Completions |

Copy [models.direct.example.json](configs/models.direct.example.json) or [models.openrouter.example.json](configs/models.openrouter.example.json) to `benchmark/configs/models.local.json`. Keep only the models you want, replace the example IDs with exact available model versions, and fill in reviewed prices per million tokens and the date checked. Null prices and placeholder identifiers intentionally fail validation. Prices are not silently fetched or substituted during a round.

For OpenRouter, select an explicit provider slug; provider fallback is disabled. Use `budget_group` to give direct and routed configurations of the same model a shared USD 20 allowance. Model IDs must be unique within a round. Native and routed results remain separate rows.

Set credentials in your shell or GitHub Actions secrets. They never belong in model JSON. Then prepare a configuration; this command does not make API calls:

```sh
python3 -m benchmark prepare-live --category all --models benchmark/configs/models.local.json --budget 100 --output benchmark/configs/pilot.local.json
python3 -m benchmark plan --config benchmark/configs/pilot.local.json
python3 -m benchmark run --config benchmark/configs/pilot.local.json --output results/live-pilot --live
```

Use `--category all` to share the USD 20 per-model allowance across all five categories in one campaign. Use `--category themes`, `plugins`, `fixes`, `performance` or `accessibility` to select a category round with its three tasks. Budgets belong to the output directory, not the provider account: use the single `all` campaign and resume it to keep the total allowance across categories. Starting a new directory establishes a separate budget. The smaller 36-run simulated pilot remains a separate configuration.

The USD 100 round budget permits up to USD 20 for each of five distinct models; it is a ceiling, not a spending target. The configuration also limits each execution to USD 1, 300 seconds, 16 API calls and 250,000 cumulative tokens by default. These limits include the skill prompt and all tool iterations. An exhausted model is skipped while other models with remaining budget can continue. Configuration validation rejects per-model limits above USD 20.

Allowed generation parameters are explicit per adapter. Unsupported options fail locally; model-specific restrictions returned by the API remain visible as provider failures. OpenAI encrypted reasoning items, Claude tool blocks and Gemini thought signatures are retained in memory for subsequent calls. Model reasoning text is not written into artifacts.

Direct-provider costs are **estimates from recorded usage and configured prices**; OpenRouter costs use its reported `usage.cost`. Cached input is treated as a subset and reasoning output is not counted twice. Cache-specific rates can be configured; omitted cache-write rates use a conservative fallback. Use upper-tier rates for models with tiered long-context pricing. The runner reserves a conservative request estimate before sending a call and stops if usage becomes uncertain. Incorrect price inputs, provider surcharges, or an in-flight request can make actual billing differ from the local estimate; configure a provider-side spending cap where available if an exact billing ceiling is required.

### First GPT-6 Astra run

[gpt-6-astra-first.json](configs/gpt-6-astra-first.json) compares the search form task without a skill, with `accessibility`, and with `frontend-design`, applied individually. It uses one repetition per condition, medium reasoning, and Standard Responses pricing reviewed on September 7, 2026. Three executions are capped at USD 6 each, USD 18 for the round, within the USD 20 model allowance. The 64,000 cumulative token limit keeps requests below Astra's 272K long-context pricing threshold.

With `OPENAI_API_KEY` available to the process and access to `gpt-6-astra`:

```sh
python3 -m benchmark validate --config benchmark/configs/gpt-6-astra-first.json
python3 -m benchmark run --config benchmark/configs/gpt-6-astra-first.json --output results/gpt-6-astra-first --live
```

The runner reads credentials from environment variables; it does not automatically load `.env` files. The report records scores, tokens, estimated costs and timings. Each browser evaluation saves `screenshot-desktop.png` (1000px before interaction), `screenshot.png` (after keyboard checks), and `screenshot-mobile.png` (390px after interaction). These screenshots document the submitted component in a neutral test page. A single repetition is an exploratory sample, not evidence for a statistical ranking. Fixture/reference screenshots are validation artifacts, not model results.

## Tasks and scoring

| Category | Tasks | Initial skill candidates |
| --- | --- | --- |
| Themes | Single template, global palette/layout, filesystem CTA pattern | WordPress block themes; Frontend Design |
| Plugins | Sanitized setting, escaped shortcode, protected REST endpoint | WordPress plugin development; Best Practices for the REST task |
| Fixes | Zero-valued option, literal SQL search, escaped admin notice | WordPress plugin development; Best Practices for security fixes |
| Performance | Bulk post titles, bulk metadata, invalidated count cache | WordPress performance |
| Accessibility | Search form, FAQ disclosure, linked product image | Accessibility; Frontend Design |

Each task directory contains `task.json`, `prompt.txt`, `initial/`, `reference/`, `blueprint.json` and `evaluate.php`. The prompt specifies the public contract. The agent cannot read the reference solution or evaluator. Criteria have explicit weights and critical flags; success requires all critical criteria. The initial suite uses equally weighted critical criteria. Scores describe this rubric, not universal software quality.

The PHP evaluator runs against the actual WordPress API. Accessibility also runs Chromium, axe and explicit keyboard checks: an automated accessibility audit alone cannot verify a disclosure's behavior. Browser screenshots are saved as evidence. Theme checks cover block discovery, rendering and global styles; they do not measure subjective design quality or complete Site Editor workflows.

Performance measures query counts and cold/warm duration samples after a discarded warmup. A real round evaluates both the original and submitted artifact in the same job. Runs are sequential within a worker. Absolute timings on shared CI hardware are noisy; query budgets and preserved behavior determine success. PHP WASM/SQLite measurements do not establish native PHP/MySQL production performance.

The files-only tool profile deliberately excludes shell execution, browsing, global skills, memory and other agents. Skill scripts are available as reference text but cannot execute. Therefore the current suite measures instruction-guided editing of small WordPress projects, not full IDE autonomy. Do not add a skill that requires another skill or mandatory unavailable execution tools. Incompatible scenarios should remain outside the eligibility map, with the reason documented. Add larger agency projects and human design review before making broad recommendations.

## Results and resume

Each output directory contains:

- `manifest.json`: resolved configuration, task/skill contents and hashes, environment and randomized matrix.
- `runs/<id>/agent.json`: source changes, tool operations, usage and request checkpoints.
- `runs/<id>/result.json`: condition, quality, cost basis, time and status.
- `runs/<id>/evaluation/`: Playground logs, criterion evidence and screenshots where applicable.
- `category-summary.json`: category comparisons on the common task set, with coverage.
- `summary.json`, `summary.csv`, `report.md`: per-task/model/skill comparisons against the paired no-skill baseline.
- `round-status.json`: completion, exhausted budgets or uncertain billing.

Rerun the identical command with the same output directory to resume. Completed executions are never generated again. A stopped evaluation can resume from the saved model output. A changed task, skill, code, lockfile or configuration requires a new directory. Environment drift is rejected on resume; individual runner metadata remains in results.

An interrupted provider request may have incurred a charge. The runner preserves pending/uncertain requests and does not retry paid generation automatically. Resolve its billing evidence before further paid work; there is no automatic reconciliation with provider invoices. Keep the old artifact intact if a new experiment is needed. This intentionally prioritizes cost accountability over filling every cell.

Quality denominators exclude infrastructure/provider errors, while failed solutions and exhausted in-progress generations remain visible. Known costs include failed attempts. No successes means cost per success is `N/A`; missing telemetry is never zero. Compare skills on shared tasks and inspect paired repetition counts. Three repetitions support a pilot, not strong statistical conclusions. There is no global winner across categories.

## GitHub Actions

[Benchmark validation](../.github/workflows/benchmark.yml) runs configuration/unit tests, checks both reference and faulty fixtures in Playground across five category jobs, and executes/resumes the 36-run simulated pilot. It has no API secrets and makes no paid model calls.

[Benchmark live models](../.github/workflows/benchmark-live.yml) runs only through `workflow_dispatch`. Select a reviewed, committed JSON configuration under `benchmark/configs/`; `.local.json` files are ignored and must be renamed and reviewed before committing. Configure only the API secrets needed by that round. Generation and evaluation use separate process environments, so model credentials are not passed to WordPress.

To resume across jobs, supply the previous workflow run ID. Its `benchmark-live` artifact is restored, then the runner checks protocol/environment identity. Artifacts upload even when a step fails. Dependency caches never contain project state, conversations or credentials. Live workflows are serialized and do not cancel an active billable job when a new one is queued.

## API sources

The adapters were implemented against primary documentation checked on September 7, 2026. Native API contract tests use simulated responses; real model availability, authentication and billing have not been tested by the bundled CI.

- [Playground CLI](https://wordpress.github.io/wordpress-playground/developers/local-development/wp-playground-cli/)
- [OpenAI Responses migration](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [GPT-6 Astra model and pricing thresholds](https://developers.openai.com/api/docs/models/gpt-6-astra)
- [Claude tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Gemini generation](https://ai.google.dev/api/generate-content) and [function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Kimi Chat Completions](https://platform.kimi.ai/docs/api/chat)
- [GLM Chat Completions](https://docs.z.ai/api-reference/llm/chat-completion)
- [OpenRouter tools](https://openrouter.ai/docs/guides/features/tool-calling) and [usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting)
