# Practical WordPress project benchmark

The primary deliverable scenario is `agency-landing-page` v1.0.0: a complete,
editable block theme for the fictional Northline agency. The 15 smaller tasks
remain diagnostic tests. A search-form score describes that component only;
it cannot establish whether a model can deliver a complete client website.

The new `wordpress-project-v2` profile and `landing-page-v1` rubric are reported
separately from `files-only-v1` / `micro-v1`. Configurations and reports reject
mixed profiles. This pilot is exploratory, with one run per condition; it does
not support a general model or skill ranking.

## Fixed assignment

Every condition receives the same [brief](tasks/agency-landing-page/public/brief.md),
local SVG artwork, minimal block-theme scaffold and rendered reference images:

- [Desktop reference](tasks/agency-landing-page/public/reference-desktop.png)
- [Mobile reference](tasks/agency-landing-page/public/reference-mobile.png)

The reference source and final acceptance code are never sent to the model or
mounted into its Playground. Task hashes cover reference, scaffold, public
materials, fixture, rubric, and Blueprint. Change the task version when changing
the contract or frozen materials. No external image/font fetching is allowed.
All Northline artwork/copy is fictional and CC0; theme code is GPL-2.0-or-later.

The theme supplies a `benchmark-fixture/landing` pattern, front-page/index
block templates, header/footer parts and `theme.json`. Installation seeds the
pattern into a published homepage, rendered through native `post-content`.
The fixed `[benchmark_contact]` fixture is installed separately: it validates
name/email/message, verifies a nonce and stores synthetic submissions locally.
It never sends email. Styling this fixture is part of the theme assignment;
implementing a contact plugin is not.

## Tools and execution

Gemini, native OpenAI Responses, and native Anthropic Messages support this profile.
Other live adapters reject it until multimodal tools are implemented; diagnostic profiles still support
all adapters. The model receives file list/read/search/write/delete tools,
a viewport screenshot plus accessible DOM, restricted browser actions, public
checks, and `submit`. Reads are bounded to 16,000 characters; search returns at
most 40 literal matches. Browser actions support local navigation, CSS-selector
click/fill, keyboard, bounded scroll and desktop/mobile viewport selection.
There is no arbitrary JavaScript, shell, host filesystem mount or external
browser navigation. PHP runs inside WASM with networking disabled; browser
requests are limited to the current site. Preview processes receive no API keys.

Each run owns its preview instance. Source changes resync the theme and reseed
its page. Browser-only actions preserve that preview's state until the next
source change. Public checks expose activation, PHP errors, native editor block
validity and basic Axe evidence, not final acceptance assertions. The model
can inspect screenshots returned by tools as native provider image inputs.

Gemini `countTokens` receives the actual outgoing `generateContentRequest`,
including system instructions, tools, images and replayed thought signatures.
Counts are not inferred from duplicated internal message representations.
Reservations use configured rates and maximum output before dispatch. Context,
cumulative-token, monetary, output-truncation, provider, preflight and tool
failures have distinct statuses. Unknown billing remains reserved; requests
are never automatically retried. `submit` freezes all file/tool actions and
ends generation. Normal model completion also ends generation.

## Acceptance rubric

| Dimension | Weight | Checks |
| --- | ---: | --- |
| WordPress integration and editability | 30 | Activation 5, native blocks 10, editor handover 15 |
| Requirements and functionality | 25 | Sections 10, CTA 5, contact form 10 |
| Accessibility | 20 | Axe 10, keyboard journey 10 |
| Responsive behavior | 15 | Layout/overflow 8, mobile navigation 7 |
| Technical quality | 10 | Errors 3, assets 3, resources 2, security 2 |

The versioned [task manifest](tasks/agency-landing-page/task.json) publishes
critical criteria. Activation, native content/editability, required sections,
CTA/form, keyboard/mobile navigation, responsive overflow, broken required
assets and security failures prevent an artifact pass regardless of score.
Axe and runtime/resource checks also contribute weighted points.

Final evaluation starts from a fresh Playground installed from the exact
`theme.zip` inside the exported `playground-bundle.zip`. It submits randomized
synthetic form values, verifies storage and invalid requests, and edits the
headline, image and CTA through the WordPress visual editor's native controls.
It clicks Save, reloads the editor, then checks the published page. Native
block validity is checked using WordPress's editor parser, not just PHP parsing.
The handover uses the heading's editable text, the image Replace control, and
the button's text/link controls. It never edits the database directly.

Desktop/mobile screenshots show the original deliverable. Additional screenshots
record form submission, editor save/reload and the changed published page.
Responsive checks include 360, 390, 768 and 1280 pixel widths. Resource budgets
are 1 MB theme source and 45 frontend requests; this is not a production hosting
performance measurement. No pixel-similarity score substitutes for behavior.

Three outcomes are always distinct:

- **Artifact pass:** all critical acceptance checks pass.
- **Execution completion:** the agent submitted or finished normally.
- **Delivery success:** artifact pass and execution completion.

A useful artifact from an interrupted run can pass acceptance without becoming
a successful delivery. Failures retain their cost and evidence.

## Human visual review

`deliveries.html` shows the brief/reference, sites, criterion evidence, costs,
tokens, iterations/timing, source diffs, theme/Playground packages and editor
screenshots. `blind-review/` is a separate pack with random site IDs and no model
or skill labels; give reviewers only that folder. The private mapping stays in
`review-map.json` outside it. Visual scoring never affects the automated score.

Reviewers score fidelity, hierarchy, typography/spacing and responsive polish
from 0–4 each. Copy `scores-template.json`, provide a human reviewer identifier,
and fill the scores. Missing reviews remain **pending**, not zero or approved.

```bash
python -m benchmark review results/landing-mock --scores /path/to/reviewed-scores.json
```

Import validates all dimensions and regenerates reports. Preserve the original
review input for provenance. Reviewers must not infer labels from the main report.

## Validation and running

```bash
python -m benchmark sync-skills
python -m benchmark validate --config benchmark/configs/landing-page.json
python -m unittest discover -s benchmark/tests -v
python -m benchmark verify-project-tools --output results/landing-tools
python -m benchmark verify-project --output results/landing-audit
python -m benchmark run --config benchmark/configs/landing-page-mock.json --output results/landing-mock
```

The audit tests the reference and starter plus static HTML replacement, broken
CTA, invalid blocks, inaccessible mobile navigation, horizontal overflow,
missing artwork, and failed form submission. Each variant must fail its target
criterion and artifact acceptance. Randomized submission/editor values catch
constant-output implementations. This follows [WP-Bench's](https://github.com/WordPress/wp-bench)
behavioral-contract/reference/assertion-audit methodology, adapted to complete
WordPress deliverables. The new CI job runs without model API credentials.

The ready live config uses Gemini 3.8 Flash, medium thinking, baseline,
`wp-block-themes`, and `frontend-design` individually at pinned revisions.
Per execution: 900 seconds, 40 calls, 32,768 output tokens per call, 1 million
cumulative tokens and US$6. Round cap: US$18; model lifetime allowance: US$20.
Set `GEMINI_API_KEY` in the process environment; the CLI does not auto-load `.env`.

```bash
python -m benchmark plan --config benchmark/configs/landing-page.json
python -m benchmark run --config benchmark/configs/landing-page.json --output results/landing-live --live
```

`results/model-budget-ledger.json` is shared across output directories and locked
for live rounds. Prior local checkpoints are imported once by manifest/run ID;
`budget-history.json` seeds known earlier pilot costs and unresolved reservations.
A full per-run reservation is written before generation and survives a crash.
After generation, known costs replace it while uncertain calls retain their
reservations. Do not delete the ledger to retry, or reset `budget_group` to bypass
an allowance. Native and routed identifiers must share a canonical model account.

CI restores the newest `benchmark-model-budget` artifact across workflow runs.
Missing or expired prior CI history blocks paid calls until reconciled. The
ledger is uploaded even after failure, with 90-day retention; archive it before
expiry. CI and independent local machines do not share a transactional database:
transfer/merge the latest ledger before changing execution hosts, and do not run
paid rounds simultaneously on separate hosts. This milestone retains WP 6.9,
PHP 8.3 and Playground 3.1.52; newer WP-Bench API scenarios are not imported.

## Five-category roadmap

| Category | Practical scenario |
| --- | --- |
| Themes | Agency landing page — implemented first |
| Plugins | Complete plugin configuration, permissions and frontend workflow |
| Fixes | Diagnose and repair a seeded site regression without breaking other journeys |
| Performance | Optimize a seeded site with repeatable before/after behavior and measurements |
| Accessibility | Remediate a complete keyboard, screen-reader and responsive user journey |

Each future scenario needs its own brief, public development tools, hidden
acceptance contract, reference solution and deliberately broken variants before
it can contribute quality claims.

### Astra and Fable pilot

`configs/landing-page-astra.json` and `configs/landing-page-fable.json` use
`gpt-6-astra` and `claude-fable-5-1` respectively, with medium reasoning and the
same three individual conditions. Each execution is capped at US$5.40 and each
round at US$16.20, under the shared US$20 lifetime allowance per model. Existing
Astra reservations remain charged against that allowance.

Both adapters send reference images and preview screenshots as native image
content, replay native reasoning unchanged, and count the actual input using
`/responses/input_tokens` or `/messages/count_tokens` before each generation.
Astra long-context pricing applies above 272,000 input tokens. Unsupported
adapters still fail before generation. These pilots remain exploratory.

For Anthropic keys that span workspaces, set `ANTHROPIC_WORKSPACE_ID` alongside
`ANTHROPIC_API_KEY` in the process environment. The adapter sends it only as the
`anthropic-workspace-id` header, including token preflight. Workspace-scoped keys
can omit it. Credentials and workspace headers are never given to model tools.

### Navigation audit caveat

The first Astra pilot exposed two limitations in `landing-page-v1`: the keyboard
journey compared raw text (including decorative arrows), and the CTA check could
run before smooth scrolling finished. Preserve original scores. The separate
`navigation-observation-v2` audit matches the CTA with an optional decorative
arrow, checks real focus/keyboard activation, and waits for navigation to settle.
It passes the reference and rejects the deliberately broken CTA. It does not
replace the scoring version, complete interrupted runs, or provide human visual
approval. Reports link audit evidence when present beside each execution.

```bash
node benchmark/environments/navigation-audit.mjs \
  ROUND/runs/RUN/evaluation/playground-bundle.zip \
  ROUND/runs/RUN/navigation-audit-v2.json
python -m benchmark report ROUND
```
