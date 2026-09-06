# Contributing

Help keep this collection useful for people developing with WordPress. Relevant general web skills are welcome alongside WordPress-specific resources.

## Suggest an entry

Open a pull request with:

- A direct link to the maintainer's repository, `SKILL.md`, or official product documentation.
- The resource name and maintainer. Clearly distinguish a community project from a vendor's integration.
- One concise description of what it does and why a WordPress developer would use it.
- Its category: agent skill, skill collection, MCP server, adapter, plugin, or hosted integration.
- Material requirements: supported runtimes, client capabilities, authentication, paid plans, or beta status.
- The date you checked the source and whether you only reviewed documentation or also tested it.

Use this format for skill entries:

```markdown
- [Resource name](https://example.com/primary-source) — **Maintainer.** What it helps a WordPress developer do. Relevant limitation.
```

For MCP integrations, follow the existing table columns. Do not put a server in the skills section merely because an agent can use it.

## Selection criteria

Entries should have public documentation, an identifiable maintainer, and implemented functionality relevant to WordPress work. For skills, inspect the actual `SKILL.md`; a directory listing alone is not sufficient evidence.

Prefer the original source over mirrors, forks without a distinct purpose, and directory aggregators. Check migration and deprecation notices. Popularity is useful context, but installation counts and stars do not establish quality or security.

Exclude placeholder projects, unsupported feature claims, generic link dumps, and affiliate links. Label beta or experimental resources. Describe a specific reason to include overlapping tools. Link to upstream material instead of copying its instructions or code.

## Languages

Update these editions together, retaining the same entries, links, commands, and limitations:

- [English](README.md)
- [Spanish](README.es.md)
- [Brazilian Portuguese](README.pt-BR.md)

Keep product names, skill identifiers, CLI commands, and URLs unchanged. Translate headings and update their table-of-contents anchors. Use the [WordPress pt-BR glossary](https://translate.wordpress.org/locale/pt-br/default/glossary/) and [Brazilian translation guidance](https://br.wordpress.org/team/handbook/traducao/boas-praticas/) for Brazilian Portuguese terminology.

If you cannot translate an addition, open an issue with the suggestion template and the source evidence so a contributor can help before it is merged. Use the same page to report a broken link, an archived project, or a mismatch between editions.

## Before submitting

- Open each new source link and check that it supports the description.
- Confirm that relative links and table-of-contents anchors work in all three READMEs.
- Keep descriptions concise and avoid copied marketing text, unverifiable superlatives, and changing popularity counts.
- Add material migrations, exclusions, or research limitations to [SOURCES.md](SOURCES.md).
- Run `git diff --check` to catch whitespace issues.

## Automated PR checks

The [validation workflow](.github/workflows/validate.yml) runs on every pull request, pushes to `main`, a weekly schedule, and manual dispatch. The scheduled run catches link rot and upstream skill changes between contributions. Three independent checks report formatting, broken links, and invalid skill sources. No personal access token is needed for PRs, including fork PRs; the workflow uses GitHub's read-only token.

- **Markdown formatting:** markdownlint checks every Markdown file, including PR templates. Long lines and compact table spacing are allowed by the repository configuration.
- **Links and anchors:** Lychee checks HTTP responses, local files, and heading anchors. Redirects are followed and temporary failures retried; HTTP errors are not treated as successful checks. Code-block examples are excluded.
- **Agent Skill sources:** the Python validator checks catalog entries between the `skills:start` and `skills:end` comments in each README. It requires matching skill names and URLs in all editions, and the same link destinations and code examples across the whole document; only translated heading anchors may differ. Each primary skill link must be a public GitHub `SKILL.md`, a directory containing one, or a repository containing one. Files must have YAML `name` and `description` strings and an instruction body. This verifies basic structure, not quality or safety. MCP and supporting documentation links only need to pass the link check.

Place new skill bullets inside the markers, starting with the linked skill name. Keep secondary website links in the description. Use a direct `SKILL.md` link when possible; a collection link only proves that at least one valid skill exists. To support another hosting provider, extend the validator with regression tests instead of adding a bypass.

Run the same checks locally with Node.js/npm, Python 3.12+, and Lychee 0.24.2 installed:

```sh
npx markdownlint-cli2@0.23.2 '**/*.md' '.github/**/*.md'
lychee --config lychee.toml --no-progress '**/*.md' '.github/**/*.md'
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_skills.py
```

For the live skill check, an optional `GITHUB_TOKEN` environment variable increases GitHub API limits. Never commit a token. A failed external request may mean a rate limit or outage rather than a removed resource; inspect the job output and rerun once the upstream problem is resolved.

[Dependabot](.github/dependabot.yml) opens weekly pull requests for the pinned GitHub Actions and the validator's Python dependencies.

To prevent merging failed checks, a maintainer must select **Markdown formatting**, **Links and anchors**, and **Agent Skill sources** as required status checks in the repository's branch rules after the workflow has run.

Contributions to the original directory text use this repository's [MIT License](LICENSE). Linked resources keep their own licenses.
