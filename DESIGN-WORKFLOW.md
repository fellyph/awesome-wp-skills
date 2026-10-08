# Design-to-WordPress workflow: skills, MCP, and quality control

This guide documents a reproducible workflow from a visual reference to a validated WordPress theme. It was created for [issue #5](https://github.com/fellyph/awesome-wp-skills/issues/5) to complement the catalog's [suggested combinations](README.md#suggested-combinations) with concrete architectural decisions, verification steps, and observed limits.

## Community reports vs. repository-tested workflow

This document separates two levels of evidence:

- **Community-reported workflows (not executed as an end-to-end bundle by this project):** In comments on the maintainer's post, Alexander Rodrigues Silva described combining Canva, Google Stitch, and Google Antigravity via MCP; Guga described building a hybrid theme with visual layout review; Gabriel Pacheco highlighted the need for quality control in WordPress agent workflows; Rafael M. Ehlers requested a step-by-step process guide; and Gustavo Mathias asked how the theme developer's role changes when agents generate layouts.
- **Repository-tested workflow (verified in this repository):** Primary documentation and local MCP tool schemas were inspected on **October 8, 2026**, and the implementation, browser inspection, editor-handover, accessibility, and runtime checks below are grounded in the repository's reproducible [agency landing-page benchmark](benchmark/LANDING-PAGE.md) (`wordpress-project-v2` / `agency-landing-page` v1.0.0) running on WordPress Playground.

## 1. Tools, official sources, and layer boundaries

An effective workflow separates the **agent client**, **MCP servers**, and **agent skills**. They are not interchangeable:

| Layer | Role in the workflow | Examples and official sources | Access requirements and limitations |
| --- | --- | --- | --- |
| **Agent client / IDE** | Hosts the model session, loads local `SKILL.md` files, manages file edits, and connects to configured MCP servers. | [Google Antigravity](https://antigravity.google/docs), Claude Code, Cursor, VS Code | Requires a supported model account/API key and local workspace permissions. Sandbox and network rules vary by client. |
| **Design MCP servers** | Expose external design canvases, tokens, or generated UI screens to the client via [MCP](https://modelcontextprotocol.io/docs/getting-started/intro). | [Google Stitch](https://stitch.withgoogle.com/), [Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server), [Canva Developers](https://www.canva.dev/) | Require vendor authentication and plan/quota eligibility. None of these servers output production WordPress block themes directly; they supply visual references, HTML/CSS prototypes, or design tokens. |
| **Browser & WordPress MCP / CLI** | Run the WordPress site, exercise the visual editor and frontend in a real browser, and capture runtime traces. | [WordPress Playground CLI](https://wordpress.github.io/wordpress-playground/developers/local-development/wp-playground-cli/), [Playwright MCP](https://github.com/microsoft/playwright-mcp), [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp), [WordPress MCP Adapter](https://github.com/WordPress/mcp-adapter) | Require Node.js and Chromium/Chrome. Playground runs PHP in WebAssembly with SQLite (`PHP WASM / SQLite`). WordPress MCP Adapter requires WordPress 6.9+ and PHP 7.4+. |
| **Agent skills (`SKILL.md`)** | Provide task-specific instructions, architectural constraints, and checklists inside the prompt context. | [wp-block-themes](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-block-themes/SKILL.md), [wp-patterns](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-patterns/SKILL.md), [Impeccable](https://github.com/pbakaus/impeccable), [Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md), [Accessibility](https://github.com/addyosmani/web-quality-skills/blob/main/skills/accessibility/SKILL.md), [a11y-debugging](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/skills/a11y-debugging/SKILL.md), [wp-performance](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-performance/SKILL.md) | Markdown instructions only; skills do not grant browser or site access unless paired with CLI or MCP tools. |

### Case study inspection: Stitch, Canva, and Antigravity via MCP

Inspecting the primary documentation and MCP tool definitions clarifies what each integration actually does:

1. **Google Stitch + Antigravity MCP:** [Stitch](https://stitch.withgoogle.com/) is an experimental Google Labs UI design tool that generates and refines mobile/desktop screens and design systems from text prompts or `DESIGN.md` specifications. When connected to [Google Antigravity](https://antigravity.google/docs/mcp) as an MCP server, it exposes project and screen tools:
   - Project & system tools: `create_project`, `list_projects`, `get_project`, `upload_design_md`, `create_design_system_from_design_md`, `create_design_system`, `update_design_system`, `apply_design_system`, `list_design_systems`.
   - Screen generation & inspection tools: `generate_screen_from_text`, `edit_screens`, `generate_variants`, `list_screens`, `get_screen`.
   - **Operational limits:** `generate_screen_from_text` can take several minutes per screen. Its tool contract explicitly instructs agents not to retry on timeout and instead poll `get_screen` every 30 seconds (up to 10 attempts). Output is a UI design/prototype, not a WordPress block theme; translating the screen into `theme.json`, templates, and valid block markup remains a separate engineering step.
2. **Canva MCP distinction:** [Canva Developers](https://www.canva.dev/) documents two separate MCP servers: the assistant-facing **Canva MCP server** (`https://mcp.canva.com/mcp`) for searching, generating, and exporting user designs and brand kit assets, and the **Canva Dev MCP server** for building Canva apps with the Canva SDK. For a WordPress theme workflow, Canva can supply brand colors, typography choices, or exported graphics, which still need to be optimized as local theme assets and mapped into `theme.json`.

## 2. Architectural decisions: theme type, editability, and plugin boundaries

Before prompting an agent to write code, the developer must define three boundaries. Leaving these implicit is the most common cause of fragile agent output.

### Block theme vs. hybrid theme

| Decision factor | Full block theme (`wp-block-themes`) | Hybrid theme (classic PHP + block support) |
| --- | --- | --- |
| **Primary mechanism** | `theme.json` + HTML block templates (`templates/*.html`), template parts (`parts/*.html`), and block patterns (`patterns/*.php`). | PHP templates (`front-page.php`, `single.php`) combined with `theme.json`, `add_theme_support( 'block-template-parts' )`, and registered block patterns. |
| **When to choose** | New marketing sites, agency landing pages, editorial sites, and greenfield projects targeting WordPress 6.9+ where editors manage full layouts in the Site Editor. | Existing classic themes undergoing gradual modernization, or projects heavily coupled to PHP template hooks and legacy meta-box workflows. |
| **Agent pitfall to avoid** | Dumping raw static `<section>` HTML or `<style>` tags into `templates/front-page.html` instead of native `<!-- wp:... -->` blocks and `theme.json` presets. | Mixing hardcoded PHP copy with block content so editors cannot tell which sections are editable in the WordPress admin. |

### Editable content vs. static template chrome

A visually faithful screenshot is not sufficient if a content editor cannot update the headline, hero image, or call-to-action (CTA) button without editing code:

- **Editable content (`post-content` + patterns):** Hero headlines, body copy, service cards, testimonials, pricing tables, feature imagery, and CTA text/links belong in native blocks (`core/group`, `core/columns`, `core/heading`, `core/paragraph`, `core/image`, `core/buttons`) registered as a block pattern (`patterns/landing.php`) and seeded into a page's `post_content`.
- **Static template chrome (`parts/` and `templates/`):** Site-wide header (`parts/header.html`), navigation landmark, footer (`parts/footer.html`), and the `<!-- wp:post-content /-->` wrapper belong in block template parts and templates.
- **Disallowed shortcuts:** Do not accept `core/html` blocks for standard text/buttons or CSS `content:` pseudo-elements for copy. Every serialized block comment must match the HTML attributes inside its body, or the WordPress block editor will display **"This block contains unexpected or invalid content."**

### Theme vs. plugin responsibilities

| Concern | Belongs in the theme | Belongs in a plugin |
| --- | --- | --- |
| **Design tokens & layout** | Color palette, fluid typography, spacing scale, layout widths (`contentSize`, `wideSize`), and element styles in `theme.json`. | Never override global site typography or layout containers from a functional plugin. |
| **Forms & submissions** | Visual styling of form fields, labels, focus rings, buttons, and status messages using `theme.json` variables. | Form shortcode/block registration, CSRF nonce verification, server-side sanitization/validation, rate limiting, and database storage. |
| **Data & custom structures** | Presentation templates and query-loop patterns for custom post types. | Registering custom post types, taxonomies, REST API endpoints (`wp-rest-api`), and custom abilities (`wp-abilities-api`). |

## 3. Minimal reproducible example

This walkthrough uses the repository's CC0/GPL-2.0 **Northline agency landing-page** fixture so every step can be reproduced locally without paid external design seats.

### Step 1: Prepare the design inputs and tokens

- **Inputs:**
  - Design brief and section specification: [`benchmark/tasks/agency-landing-page/public/brief.md`](benchmark/tasks/agency-landing-page/public/brief.md)
  - Desktop visual reference (`1280×800`): [`benchmark/tasks/agency-landing-page/public/reference-desktop.png`](benchmark/tasks/agency-landing-page/public/reference-desktop.png)
  - Mobile visual reference (`390×844`): [`benchmark/tasks/agency-landing-page/public/reference-mobile.png`](benchmark/tasks/agency-landing-page/public/reference-mobile.png)
  - Starter block-theme scaffold and local SVG artwork: [`benchmark/tasks/agency-landing-page/initial/`](benchmark/tasks/agency-landing-page/initial/)
- **Optional Stitch / Figma pre-step:** If starting from a new concept in Stitch or Figma, export the desktop (`1280px`) and mobile (`390px`) reference PNGs plus a `DESIGN.md` token summary (brand hex colors, heading/body font families, container widths, and required page sections).
- **Human intervention required:** Verify that all color pairs in the palette meet WCAG 2.1 AA contrast (`4.5:1` for normal text, `3:1` for large text/UI components) before locking `theme.json`, and ensure all SVG/image assets are local and licensed for distribution.

### Step 2: Set up the local environment and skills

Install dependencies and fetch the locked skills from the repository root:

```sh
npm ci --ignore-scripts
npx playwright install chromium
python3 -m benchmark sync-skills
```

To install the same upstream skills in your own WordPress theme repository with the Skills CLI:

```sh
npx skills add WordPress/agent-skills --skill wp-block-themes
npx skills add WordPress/agent-skills --skill wp-patterns
npx skills add addyosmani/web-quality-skills --skill accessibility
```

### Step 3: Prompt the agent to implement the block theme

Provide the brief, reference images, and active skill (`wp-block-themes`) with explicit architectural constraints:

```text
Implement the Northline agency block theme in the current theme directory using the visual brief and desktop/mobile reference images.

Requirements:
1. Define palette, typography, spacing, and layout presets in theme.json (no external fonts or remote assets).
2. Keep header and footer in parts/header.html and parts/footer.html, and render the front page through native post-content in templates/front-page.html.
3. Implement all required sections (header navigation, hero with local SVG artwork and primary CTA linking to #contact, services grid, proof/metrics, process steps, testimonial, and #contact section wrapping [benchmark_contact]) inside patterns/landing.php using valid core block markup.
4. Keep the hero headline, hero image, and primary CTA editable via native Gutenberg controls without block recovery warnings.
```

- **Deliverables:** `style.css`, `functions.php`, `theme.json`, `templates/index.html`, `templates/front-page.html`, `parts/header.html`, `parts/footer.html`, `patterns/landing.php`, and local `assets/images/*.svg`.

### Step 4: Run automated browser, editor-handover, and accessibility checks

Verify the preview toolchain and run the full acceptance and negative-variant audit in WordPress Playground:

```sh
python3 -m benchmark verify-project-tools --output results/landing-tools
python3 -m benchmark verify-project --output results/landing-audit
```

To run the complete simulated project workflow and generate the visual comparison report (`results/landing-mock/deliveries.html`):

```sh
python3 -m benchmark run --config benchmark/configs/landing-page-mock.json --output results/landing-mock
```

## 4. Quality control: responsiveness, accessibility, content editing, and browser behavior

An agent-generated WordPress theme should pass four verification gates before human sign-off:

1. **Responsive behavior across viewports (`360px`, `390px`, `768px`, `1280px`):**
   - Confirm zero horizontal overflow (`document.documentElement.scrollWidth <= window.innerWidth`) at every width.
   - Verify that multi-column service and metric grids stack cleanly on `360px` and `390px` screens without clipped text or overlapping buttons.
   - Exercise mobile navigation at `390px`: if a disclosure toggle is used, verify it exposes `aria-expanded`, opens/closes via keyboard (`Enter`/`Space`), and keeps links reachable.
2. **Accessibility (`Accessibility` + `a11y-debugging`):**
   - Run `axe-core` against the rendered homepage and verify zero critical or serious WCAG violations (color contrast, form `<label>` associations, heading hierarchy, landmark roles).
   - Execute a real keyboard journey (`Tab` and `Shift+Tab`) from the top of the document through navigation links, the primary hero CTA, and every contact form input/button. Verify that `:focus-visible` outlines remain visible and pressing `Enter` on the primary CTA navigates to `#contact`.
3. **Content editing and Gutenberg handover:**
   - Open the seeded homepage in the WordPress block editor (`/wp-admin/post.php?post=<id>&action=edit`).
   - Parse blocks using WordPress's editor block parser (`wp.blocks.parse`) and confirm zero invalid blocks or recovery warnings.
   - Edit the hero `H1` text, replace the hero image via the native **Replace** control, and change the primary button label and URL using native block controls. Click **Save**, reload the editor, and load the public homepage to confirm the changes persist.
4. **Browser functionality and plugin integration:**
   - Submit the `[benchmark_contact]` form with an invalid email to verify error handling, then submit valid synthetic input to verify nonce validation, storage, and the rendered confirmation notice.
   - Inspect browser `console` and `pageerror` events plus network responses to ensure zero uncaught JavaScript exceptions, zero PHP warnings/fatals, and zero broken local SVG/CSS requests.

## 5. Visual screenshot feedback vs. runtime performance measurements

Agent workflows often capture screenshots to critique a page. Keep **visual inspection** and **runtime performance measurement** strictly separate:

| Dimension | Screenshot review (static image) | Runtime measurement (live site in browser) |
| --- | --- | --- |
| **What it can detect** | Visual hierarchy, alignment, spacing balance, broken image placeholders, text clipping, and obvious layout collisions at one frozen state. | Resource transfer size, request count, render-blocking CSS/JS, Largest Contentful Paint (LCP), Interaction to Next Paint (INP), Cumulative Layout Shift (CLS), and backend SQL query counts. |
| **What it cannot prove** | Cannot measure loading speed, font swap shifts, scroll jank, JavaScript main-thread blocking, PHP/database bottlenecks, or keyboard focus traps. | Automated timing and resource metrics do not judge brand fit, aesthetic polish, or copy clarity. |
| **Tools to use** | Multimodal preview screenshots (`screenshot-desktop.png`, `screenshot-mobile.png`) + blinded human visual review (`0–4` rubric). | [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) traces, Playwright network/timing inspection, and [wp-performance](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-performance/SKILL.md) / WP-CLI profiling. |

### Recorded measurement conditions and results in this repository

- **Environment and conditions:** WordPress 6.9, PHP 8.3 (WebAssembly), SQLite, `@wp-playground/cli` 3.1.52, and headless Chromium via Playwright 1.63.0 / `axe-core` 4.13.0 on macOS (`arm64`) and Ubuntu 24.04 CI runners.
- **Practical landing-page resource checks (`agency-landing-page` v1.0.0):** The acceptance harness enforces a theme source budget of `<= 1 MB`, `<= 45` total frontend HTTP requests, zero external asset requests, and zero HTTP `>= 400` responses. The reference solution and passing model snapshots ([`gpt-6-astra` `no-skill`](benchmark/results/gpt-6-astra/latest/README.md) and [`claude-fable-5-1` `no-skill`](benchmark/results/claude-fable-5-1/latest/README.md)) pass all asset and resource checks in ~41–51 seconds of full browser + editor evaluation.
- **Diagnostic backend performance checks (`files-only-v1`):** For backend bottlenecks (N+1 queries, metadata priming, cache invalidation), the runner discards a warmup request and records SQL query counts plus cold/warm execution durations in the same job. Because WordPress Playground runs PHP in WebAssembly over SQLite, query budgets and behavioral assertions determine pass/fail—**Playground timings are not production native PHP/MySQL hosting benchmarks.**

## 6. Conversion optimization suggestions are hypotheses

When a design skill (`Impeccable`, `Frontend Design`, `Web Design Guidelines`) or a multimodal model reviews a screenshot and suggests moving a CTA above the fold, increasing button contrast, shortening a form, or rewriting social proof copy, treat those recommendations as **conversion rate optimization (CRO) hypotheses to validate**, never as proven conversion gains:

- A screenshot review or heuristic checklist cannot measure user intent, traffic quality, or actual form-completion rates.
- Before claiming a conversion improvement, instrument the live WordPress site (for example, tracking `#contact` anchor activations and successful form submissions) and validate the change against baseline traffic with real users.

## 7. Manual adjustments, observed consumption, and workflow limits

Across the repository's live exploratory runs ([`benchmark/results/README.md`](benchmark/results/README.md)), combining models, skills, and browser preview tools surfaced concrete operational limits where human developer intervention remains essential:

| Model and condition (`agency-landing-page`) | Tokens / API calls | Known cost (USD) | Automated score | Outcome and required manual intervention |
| --- | --- | ---: | ---: | --- |
| `gpt-6-astra` (`no-skill`) | 745,863 / 29 | $2.364737 | 100.0 | Passed all 14 automated checks (`delivery_success: True`); human visual review (`0–4`) still required before client delivery. |
| `gpt-6-astra` (`wp-block-themes`) | 718,759 / 26 | $2.787952 | 85.0 | Stopped at per-run `monetary_limit`; appended a decorative arrow (`→`) to the CTA label and used smooth scrolling, which failed the strict `landing-page-v1` text/scroll check but passed the post-run `navigation-observation-v2` audit. |
| `gpt-6-astra` (`frontend-design`) | 398,831 / 17 | $1.582812 | 85.0 | Completed execution (`execution_completion: True`), but its decorative CTA arrow and smooth-scroll timing required the same manual CTA/scroll adjustment or supplemental navigation audit. |
| `claude-fable-5-1` (`no-skill`) | 109,609 / 9 | $1.615850 | 100.0 | Artifact passed all 14 checks (`artifact_pass: True`), but generation hit the per-run monetary reservation cap on a subsequent turn (`delivery_success: False`). |
| `claude-fable-5-1` (`wp-block-themes`) | 85,286 / 5 | $1.443540 | 70.0 | Stopped at `monetary_limit` before completing Gutenberg editor-handover and CTA requirements; requires manual template/pattern completion. |
| `claude-fable-5-1` (`frontend-design`) | 117,191 / 7 | $1.761150 | 70.0 | Stopped at `monetary_limit` with incomplete editor-handover and CTA wiring. |

### Summary of developer responsibilities

1. **Budget and context management:** Multimodal turns that replay reference images, preview screenshots, and lengthy `SKILL.md` references consume 85,000–745,000 tokens per run. Developers must scope prompts tightly and set explicit per-run and per-model cost ceilings (`USD 5.40–6.00` per run under the repository's `USD 20.00` per-model allowance).
2. **Block grammar and editor recovery fixes:** Even when a frontend screenshot looks polished, developers must inspect `patterns/*.php` and `templates/*.html` in the Gutenberg editor to eliminate block serialization mismatches and hard-coded non-editable markup.
3. **Interactive timing and accessibility edge cases:** CSS `scroll-behavior: smooth`, decorative glyphs inside interactive labels, and custom mobile menu toggles require manual verification with keyboard navigation and assistive technology.
4. **Final editorial and visual sign-off:** Automated checks verify structural contracts; human reviewers remain responsible for brand fidelity, typography/spacing nuance, copy accuracy, and production deployment.
