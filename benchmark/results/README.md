# Published benchmark snapshots

This directory keeps the latest safe, tracked snapshot for each model. It contains submitted source, installable theme and Playground packages (where applicable), screenshots, public checks, and concise telemetry when an execution generated an artifact.

- [GPT-6 Astra (`wordpress-project-v2` / `themes`)](gpt-6-astra/latest/)
- [Claude Fable 5.1 (`wordpress-project-v2` / `themes`)](claude-fable-5-1/latest/)
- [Gemini 3.8 Flash (`files-only-v1` / `accessibility`)](gemini-3.8-flash/latest/)

Raw output remains under the ignored repository-root `results/` directory. It is not committed because manifests and request checkpoints may contain hidden reference material. Use `python3 -m benchmark.publish_results` after a reviewed round to replace one model's `latest` snapshot.

## Practical project comparisons (`wordpress-project-v2` / `landing-page-v1`)

Task: `themes/agency-landing-page` (`v1.0.0`). Each condition was evaluated in a fresh WordPress Playground instance from its exported `theme.zip`.

| Category / task | Model | Condition | Reps (`n`) | Score ± SD | Δ score vs no skill | Artifact pass | Execution completion | Delivery success | Known cost (USD) | USD / success | Tokens / calls | Visual review |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | ---: | --- | --- | --- |
| `themes/agency-landing-page` | [gpt-6-astra](gpt-6-astra/latest/) | `no-skill` | 1 | 100.0 ± N/A | 0.0 | True | True | True | $2.364737 | $2.365 | 745,863 / 29 | `pending` |
| `themes/agency-landing-page` | [gpt-6-astra](gpt-6-astra/latest/) | `wp-block-themes` | 1 | 85.0 ± N/A | -15.0 | False | False (`monetary_limit`) | False | $2.787952 | N/A | 718,759 / 26 | `pending` |
| `themes/agency-landing-page` | [gpt-6-astra](gpt-6-astra/latest/) | `frontend-design` | 1 | 85.0 ± N/A | -15.0 | False | True | False | $1.582812 | N/A | 398,831 / 17 | `pending` |
| `themes/agency-landing-page` | [claude-fable-5-1](claude-fable-5-1/latest/) | `no-skill` | 1 | 100.0 ± N/A | 0.0 | True | False (`monetary_limit`) | False | $1.615850 | N/A | 109,609 / 9 | `pending` |
| `themes/agency-landing-page` | [claude-fable-5-1](claude-fable-5-1/latest/) | `wp-block-themes` | 1 | 70.0 ± N/A | -30.0 | False | False (`monetary_limit`) | False | $1.443540 | N/A | 85,286 / 5 | `pending` |
| `themes/agency-landing-page` | [claude-fable-5-1](claude-fable-5-1/latest/) | `frontend-design` | 1 | 70.0 ± N/A | -30.0 | False | False (`monetary_limit`) | False | $1.761150 | N/A | 117,191 / 7 | `pending` |

### Supplemental navigation audit (`navigation-observation-v2`)

In `gpt-6-astra`, both `wp-block-themes` and `frontend-design` failed `cta` and `keyboard` under the original `landing-page-v1` rubric (85.0) because the CTA included a decorative arrow and smooth scrolling had not settled before assertion checks. Under the separate post-run `navigation-observation-v2` audit ([`wp-block-themes/navigation-audit-v2.json`](gpt-6-astra/latest/wp-block-themes/navigation-audit-v2.json), [`frontend-design/navigation-audit-v2.json`](gpt-6-astra/latest/frontend-design/navigation-audit-v2.json)), both artifacts pass CTA navigation and keyboard focus checks. Original `landing-page-v1` scores and statuses remain unchanged.

In `claude-fable-5-1`, the `no-skill` artifact passed all 14 automated checks (`100.0`, `artifact_pass: True`) before hitting the per-run monetary reservation ceiling on a subsequent turn (`execution_completion: False`, `delivery_success: False`). Both `wp-block-themes` and `frontend-design` stopped at `monetary_limit` before completing editor-handover and CTA requirements (`70.0`).

## Diagnostic component comparisons (`files-only-v1` / `micro-v1`)

Task: `accessibility/accessibility-form`. Diagnostic runs use the four-tool `files-only-v1` profile and are reported separately from `wordpress-project-v2` deliverables.

| Category / task | Model | Condition | Reps (`n`) | Score ± SD | Δ score vs no skill | Artifact pass | Execution completion | Delivery success | Known cost (USD) | USD / success | Tokens / calls |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | ---: | --- | --- |
| `accessibility/accessibility-form` | [gemini-3.8-flash](gemini-3.8-flash/latest/) | `no-skill` | 1 | 25.0 ± N/A | 0.0 | False | False (`incomplete`) | False | $0.067633 | N/A | 25,661 / 4 |
| `accessibility/accessibility-form` | [gemini-3.8-flash](gemini-3.8-flash/latest/) | `accessibility` | 1 | 25.0 ± N/A | 0.0 | False | False (`budget_exceeded`) | False | $0.061706 | N/A | 43,643 / 5 |
| `accessibility/accessibility-form` | [gemini-3.8-flash](gemini-3.8-flash/latest/) | `frontend-design` | 1 | 100.0 ± N/A | +75.0 | True | False (`budget_exceeded`) | False | $0.127940 | N/A | 66,067 / 5 |

## Scope and limitations

- **Separate profiles, no global ranking:** Diagnostic component edits (`files-only-v1`) and full block-theme deliverables (`wordpress-project-v2`) test different capabilities and are never merged into a single score.
- **Single-repetition exploratory pilots:** Published live snapshots have `n = 1` repetition per condition (`SD = N/A`) within the shared USD 20 per-model lifetime budget. They verify end-to-end execution and surface failure modes, not statistically significant rankings.
- **Distinct completion states:** `artifact_pass` (all critical acceptance criteria pass), `execution_completion` (normal model completion or `submit` within budget), and `delivery_success` (`artifact_pass` and `execution_completion`) are tracked separately. `USD / success` divides total known cost (including failed attempts) by successful deliveries and is `N/A` when `delivery_success` is zero.
- **Pending human review:** Blinded human visual review (`0–4` across fidelity, hierarchy, typography/spacing, and responsive polish) remains `pending` until human reviewer scores are imported via `python3 -m benchmark review`.
- **Playground runtime:** Evaluations run in WordPress Playground (`PHP 8.3 WASM / SQLite`, WordPress 6.9) and do not represent production native PHP/MySQL server performance.
