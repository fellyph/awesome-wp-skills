# Research notes

Initial documentation review: **2026-09-05**.

## Scope and method

The catalog currently lists 29 agent skills and 8 MCP integrations. Research was split across WordPress skills, general web skills, and MCP/site-builder integrations, then consolidated into the three READMEs.

Entries were selected from maintainer-controlled repositories and product documentation. Individual skill instructions were inspected, along with installation notes and relevant migration notices. The WordPress use cases and suggested combinations are editorial assessments of documented capabilities.

This was a source review, not an installation test, security audit, accessibility conformance assessment, or live-site benchmark. The review date records when documentation was checked, not a guarantee about future availability. Changing prices, tool counts, star counts, and installation counts are deliberately omitted from the catalog.

## Source families

The README entry links are the primary evidence for each description. These collection-level sources establish ownership and setup context:

| Source | What was checked |
| --- | --- |
| [WordPress/agent-skills](https://github.com/WordPress/agent-skills) | All 16 listed WordPress skill files, including wpds and wp-performance. Current collection targets WordPress 7.0+ and PHP 7.4+; inspect individual requirements for older projects. |
| [Impeccable](https://impeccable.style/) and [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Original repository, design skill/command distribution, and installation guidance. |
| [Addy Osmani's web-quality-skills](https://github.com/addyosmani/web-quality-skills) | Six individual skill files; collection is unofficial and stack-agnostic. |
| [Chrome DevTools skills](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Accessibility debugging instructions (a11y-debugging) using the accessibility tree, Lighthouse, and Chrome DevTools MCP. |
| [Anthropic skills](https://github.com/anthropics/skills) | Frontend design and Python Playwright web application testing instructions. |
| [Vercel agent-skills](https://github.com/vercel-labs/agent-skills) | Web design guidelines skill file. The collection's React guidance was reviewed and excluded; see below. |
| [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | Skill file, its eval checklist, README, and MIT license, reviewed on 2026-09-07. Community project by Peter Yang, also distributed as a ChatGPT/Codex plugin. Suggested by Rafael M. Ehlers in comments on the maintainer's post and evaluated in [issue #3](https://github.com/fellyph/awesome-wp-skills/issues/3). Instructions, banned-word list, and examples are in English; behavior on Portuguese or Spanish text was not assessed. The skill names patterns and does not claim to detect AI authorship. |
| [Cloudflare security-audit-skill](https://github.com/cloudflare/security-audit-skill) | Actual skill, independent validation workflow, subagent support, and Node.js requirements. |
| [Skills CLI](https://github.com/vercel-labs/skills) | Documented installation syntax; commands in the READMEs were not executed. |

## MCP requirements and status

| Source | Important distinction |
| --- | --- |
| [WordPress MCP Adapter installation](https://github.com/WordPress/mcp-adapter/blob/trunk/docs/getting-started/installation.md) | WordPress 6.9+ and PHP 7.4+. The adapter exposes abilities; it does not imply every plugin already provides them. |
| [WordPress.com MCP support](https://wordpress.com/support/mcp/) and [custom client guide](https://developer.wordpress.com/docs/mcp/connect-custom-mcp-client/) | Hosted, authenticated service with eligibility requirements. WordPress.com and eligible Jetpack-connected sites are distinct from arbitrary self-hosted installations. |
| [Elementor 4.3 beta announcement](https://github.com/orgs/elementor/discussions/37152) and [MCP documentation](https://github.com/elementor/elementor/tree/main/docs/atomic-builder/mcp) | September 1, 2026 announcement. Official integration was beta at review; administrator connection and Pro-element requirements apply. |
| [EMCP Tools readme](https://github.com/msrbuilds/elementor-mcp/blob/main/readme.txt) | Community project using MCP Adapter. WordPress 6.9+ and PHP 8.1+; distinct from Elementor's official integration. |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Browser automation through accessibility snapshots; snapshots do not establish accessibility conformance. |
| [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Browser inspection and performance tooling; Node.js and Chrome requirements are upstream. |
| [Context7](https://github.com/upstash/context7) | Documentation retrieval, with library-specific coverage and service limits. Not a universal WordPress API reference. |
| [Figma MCP guide](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server) | Design context, not direct WordPress administration. Desktop and remote access differ. |

## Migrations and exclusions

- [Automattic/agent-skills](https://github.com/Automattic/agent-skills) is archived and directs development to WordPress/agent-skills. The original block-theme recommendation now uses the maintained source.
- [Automattic/wordpress-mcp](https://github.com/Automattic/wordpress-mcp) directs users toward WordPress/mcp-adapter; it is not recommended as a separate current integration.
- [WPCursor/elementor-mcp](https://github.com/WPCursor/elementor-mcp) describes tools still to be implemented. It was excluded from this first round.
- [React Best Practices](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md) from Vercel was listed in the first round and later removed. Its guidance is framework-specific and has no distinct WordPress use case beyond generic React advice.
- [Automattic/wordpress-agent-skills](https://github.com/Automattic/wordpress-agent-skills) is a different repository with prototype theme/site workflows. Its beta/non-production status and lack of individual skill verification in this review kept it out of the initial catalog.

## Localization

English is the source edition. The Spanish and Brazilian Portuguese editions preserve the catalog, source links, setup examples, and limitations.

The Brazilian Portuguese review consulted the [WordPress glossary](https://translate.wordpress.org/locale/pt-br/default/glossary/) and [translation best practices](https://br.wordpress.org/team/handbook/traducao/boas-praticas/). Product and skill names stay unchanged. The glossary confirms “bloco” and “editor de blocos”; “acessibilidade” and “padrões” are contextual translations where the consulted glossary did not return matching entries.

## Benchmark implementation (September 7, 2026)

The [benchmark framework](benchmark/README.md) evaluates 15 focused WordPress tasks with individually applied skills. Upstream skill commits and file hashes are recorded in its lockfile; downloaded resources stay in an ignored cache. This does not change the catalog's documentation-only verification status.

Native adapters cover OpenAI, Anthropic, Gemini, Kimi and GLM, with optional OpenRouter routing. API sources and runtime limitations are documented in the benchmark guide. Provider formats and cost calculations are tested using simulated responses; no real-model quality, availability or billing results are claimed. Playground fixture tests verify reference and faulty solutions, not model performance. The initial files-only tool profile cannot run bundled skill scripts or other agents.
