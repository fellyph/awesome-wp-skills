# Awesome WordPress Agent Skills

[English](README.md) · [Español](README.es.md) · [Português do Brasil](README.pt-BR.md)

[![Validate repository](https://github.com/fellyph/awesome-wp-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/fellyph/awesome-wp-skills/actions/workflows/validate.yml)

A curated collection of agent skills and MCP integrations for people building with WordPress. Themes, plugins, blocks, accessibility, performance, design, testing, and site builders—all in one place.

Great WordPress development draws on the wider web ecosystem. This list includes both WordPress-specific expertise and general tools with a practical WordPress use case.

## Contents

- [Start here](#start-here)
- [WordPress skills](#wordpress-skills)
- [Design and frontend skills](#design-and-frontend-skills)
- [Content and writing skills](#content-and-writing-skills)
- [Accessibility, performance, and quality skills](#accessibility-performance-and-quality-skills)
- [Testing and security skills](#testing-and-security-skills)
- [MCP servers and integrations](#mcp-servers-and-integrations)
- [Suggested combinations](#suggested-combinations)
- [Model and skill benchmark](#model-and-skill-benchmark)
- [Contributing](#contributing)

## Start here

An **agent skill** packages task instructions in a `SKILL.md` file, sometimes with scripts and references. An **MCP server** gives an agent access to tools or external data. They complement each other: a skill can guide a review, while an MCP server supplies browser measurements or site access. See the [Agent Skills format](https://agentskills.io/home) and [MCP introduction](https://modelcontextprotocol.io/docs/getting-started/intro).

This repository is a directory of links, not a bundle to install. Choose the upstream skills you need and follow their setup instructions. For example, with Node.js/npm available, the [Skills CLI](https://github.com/vercel-labs/skills) supports:

```sh
npx skills add WordPress/agent-skills --skill wp-block-themes
npx skills add addyosmani/web-quality-skills --skill accessibility
```

For Impeccable, follow its [installation guide](https://impeccable.style/). MCP integrations have their own authentication, runtime, and client requirements; the commands above do not install them.

**Selection:** public primary sources, identifiable maintainers, documented functionality, and a concrete WordPress use case. Inclusion is an editorial recommendation, not certification or vendor endorsement. Source documentation was checked on **September 5, 2026**; installations and live integrations were not tested. See [research notes](SOURCES.md) for scope, migrations, and exclusions.

<!-- skills:start -->

## WordPress skills

These skills come from the maintained [WordPress/agent-skills](https://github.com/WordPress/agent-skills) collection. The former [Automattic/agent-skills](https://github.com/Automattic/agent-skills) repository is archived and points there. Check upstream version requirements before use.

### Project orientation

- [wordpress-router](https://github.com/WordPress/agent-skills/blob/trunk/skills/wordpress-router/SKILL.md) — Identifies the project type and routes work to the appropriate WordPress workflow.
- [wp-project-triage](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-project-triage/SKILL.md) — Inspects repository structure, tooling, tests, and version clues before making changes.

### Themes, blocks, and interactivity

- [wp-block-themes](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-block-themes/SKILL.md) — Builds and troubleshoots block themes, global styles, templates, and Site Editor overrides.
- [wp-block-development](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-block-development/SKILL.md) — Develops custom blocks with reliable registration, saved content, rendering, and upgrade paths.
- [wp-patterns](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-patterns/SKILL.md) — Creates reusable block patterns with theme presets, accessible markup, and correct registration.
- [wp-interactivity-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-interactivity-api/SKILL.md) — Adds interactive block behavior with WordPress directives, state, actions, and script modules.

### Plugins and APIs

- [wp-plugin-development](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-plugin-development/SKILL.md) — Guides plugin structure, settings, data handling, security checks, and release preparation.
- [wp-rest-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-rest-api/SKILL.md) — Designs REST endpoints with schemas, authorization, input validation, and predictable responses.
- [wp-abilities-api](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-abilities-api/SKILL.md) — Registers discoverable WordPress abilities and connects them to clients with appropriate permissions.
- [wp-plugin-directory-guidelines](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-plugin-directory-guidelines/SKILL.md) — Reviews naming, licensing, distribution, and monetization against WordPress.org Plugin Directory guidance.

### Operations and development environments

- [wp-wpcli-and-ops](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-wpcli-and-ops/SKILL.md) — Handles administration and maintenance through WP-CLI, including migrations and multisite tasks.
- [wp-phpstan](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-phpstan/SKILL.md) — Configures static analysis for WordPress PHP, framework types, and existing-code baselines.
- [wp-playground](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-playground/SKILL.md) — Selects Playground workflows for local execution, browser previews, snapshots, and debugging.
- [blueprint](https://github.com/WordPress/agent-skills/blob/trunk/skills/blueprint/SKILL.md) — Authors and validates repeatable Playground environments using Blueprint JSON and bundled resources.

## Design and frontend skills

- [Impeccable](https://github.com/pbakaus/impeccable) — **Paul Bakaus.** Design skill and commands for typography, layout, color, motion, and interface copy. Useful for themes, landing pages, and plugin screens. [Website](https://impeccable.style/).
- [wpds](https://github.com/WordPress/agent-skills/blob/trunk/skills/wpds/SKILL.md) — **WordPress.** Builds interfaces with WordPress Design System components, tokens, and interaction patterns.
- [Frontend Design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) — **Anthropic.** Creates distinctive layouts and components that can inform custom themes and page sections.
- [Web Design Guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md) — **Vercel.** Reviews interface code for accessible forms, focus states, motion, localization, and UX details.

## Content and writing skills

- [no-ai-slop](https://github.com/petergyang/no-ai-slop/blob/main/skills/no-ai-slop/SKILL.md) — **Peter Yang.** Edits drafts to remove repetitive AI writing patterns while keeping the author's voice, or flags the patterns without rewriting. Useful for post, page, and interface copy. Instructions and examples are in English; it is not an AI-authorship detector.

## Accessibility, performance, and quality skills

The web-quality skills below are maintained by **Addy Osmani** as an [unofficial, stack-agnostic collection](https://github.com/addyosmani/web-quality-skills), not a Google product.

- [Accessibility](https://github.com/addyosmani/web-quality-skills/blob/main/skills/accessibility/SKILL.md) — Reviews keyboard navigation, semantic HTML, contrast, and assistive technology support in rendered pages and source.
- [Performance](https://github.com/addyosmani/web-quality-skills/blob/main/skills/performance/SKILL.md) — Measures loading and runtime bottlenecks in assets, rendering, JavaScript, fonts, and caching.
- [Core Web Vitals](https://github.com/addyosmani/web-quality-skills/blob/main/skills/core-web-vitals/SKILL.md) — Investigates LCP, INP, and CLS to identify costly theme and plugin frontend behavior.
- [Web Quality Audit](https://github.com/addyosmani/web-quality-skills/blob/main/skills/web-quality-audit/SKILL.md) — Coordinates a broader review of performance, accessibility, technical SEO, and browser best practices.
- [SEO](https://github.com/addyosmani/web-quality-skills/blob/main/skills/seo/SKILL.md) — Reviews crawlability, metadata, headings, and structured data in the pages a site actually renders.
- [Best Practices](https://github.com/addyosmani/web-quality-skills/blob/main/skills/best-practices/SKILL.md) — Checks browser compatibility, runtime errors, dependencies, and web security fundamentals.
- [wp-performance](https://github.com/WordPress/agent-skills/blob/trunk/skills/wp-performance/SKILL.md) — **WordPress.** Measures backend bottlenecks in queries, caching, scheduled work, and remote requests. Complements browser performance reviews.
- [a11y-debugging](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/skills/a11y-debugging/SKILL.md) — **Chrome DevTools.** Audits and debugs accessibility using the DevTools accessibility tree, Lighthouse checks, focus state tracking, and color contrast. Requires Chrome DevTools MCP.

## Testing and security skills

- [Web App Testing](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md) — **Anthropic.** Uses Python Playwright scripts to exercise local interfaces, capture screenshots, and inspect browser logs.
- [Security Audit](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md) — **Cloudflare.** Coordinates code analysis and independent validation of findings. Requires parallel subagent support and Node.js; complements WordPress-specific review.

<!-- skills:end -->

## MCP servers and integrations

These entries provide tool access. Some run locally, some are WordPress plugins, and others are hosted services. Follow the linked documentation for setup and current eligibility.

### WordPress and site builders

| Integration | Maintainer / type | WordPress use case and requirements |
| --- | --- | --- |
| [WordPress MCP Adapter](https://github.com/WordPress/mcp-adapter) | WordPress · plugin/adapter | Exposes registered abilities to MCP clients. Requires WordPress 6.9+ and PHP 7.4+; available actions depend on exposed abilities. |
| [WordPress.com MCP](https://wordpress.com/support/mcp/) | Automattic · hosted service | Connects assistants to site content and settings. Requires an eligible WordPress.com or Jetpack-connected site and authentication; plan limits apply. |
| [Elementor MCP](https://github.com/elementor/elementor/tree/main/docs/atomic-builder/mcp) | Elementor · official integration · **beta** | Builds native Elementor pages and works with site design settings. Announced with [Elementor 4.3 beta](https://github.com/orgs/elementor/discussions/37152); administrator setup required, and Pro elements need Pro. |
| [EMCP Tools](https://github.com/msrbuilds/elementor-mcp) | msrbuilds · community plugin | Adds Elementor structure, widget, and template tools through WordPress MCP Adapter. Requires WordPress 6.9+ and PHP 8.1+; separate from Elementor's official integration. |

### Browser testing, debugging, and design context

| Integration | Maintainer / type | WordPress use case and requirements |
| --- | --- | --- |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Microsoft · browser server | Exercises admin screens, forms, and frontend behavior through browser automation. Accessibility snapshots support interaction; they are not a complete accessibility audit. |
| [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Chrome DevTools · browser server | Records performance traces and inspects requests, console output, and rendered pages. Requires a supported Node.js runtime and Chrome. |
| [Context7](https://github.com/upstash/context7) | Upstash · documentation server/service | Retrieves library documentation for frontend and tooling work. Coverage varies by library; an API key increases usage limits. |
| [Figma MCP](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server) | Figma · design service | Supplies design context for themes, blocks, and builder layouts. Remote and desktop access have different seat requirements and usage limits. |

## Suggested combinations

These are starting points, not tested bundles. Select tools for the work at hand.

| Goal | Try together |
| --- | --- |
| Build a block theme | wp-block-themes + wp-patterns + Impeccable + Accessibility |
| Develop a plugin | wp-plugin-development + wp-rest-api + wp-phpstan + Web App Testing |
| Investigate a slow site | wp-performance + Core Web Vitals + Chrome DevTools MCP |
| Work with Elementor | Elementor MCP (beta) or EMCP Tools + Accessibility + Performance |
| Build a repeatable demo | wp-playground + blueprint + Playwright MCP |
| Implement a design | Figma MCP + wpds or Frontend Design + Web Design Guidelines |
| Write a post or landing page | no-ai-slop + SEO + Impeccable |

## Model and skill benchmark

The [benchmark framework](benchmark/README.md) compares individual skills and models across themes, plugins, fixes, performance, and accessibility using WordPress Playground in CI. It includes native API adapters and OpenRouter, a USD 20 per-model budget limit, and reproducible reports. Its first [practical scenario](benchmark/LANDING-PAGE.md) delivers an editable agency landing page with a fixed visual brief, editor handover tests, screenshots and blinded human review. [Published model snapshots](benchmark/results/) retain the latest safe result for each model; raw benchmark output remains local and ignored.

## Contributing

Found a useful skill or integration? Read [CONTRIBUTING.md](CONTRIBUTING.md). Include its primary source, maintainer, WordPress use case, and any beta, plan, or runtime requirements. Keep all three language editions aligned.

This collection began with Impeccable, WordPress block-theme skills, and Addy Osmani's accessibility skill. Thanks to the maintainers who make these resources available.

## License

The original text in this directory is available under the [MIT License](LICENSE). Linked projects retain their own licenses.
