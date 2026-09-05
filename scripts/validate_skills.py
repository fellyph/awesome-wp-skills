"""Check catalog parity and public GitHub Agent Skill sources without running them."""

import base64
from collections import Counter
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen

from markdown_it import MarkdownIt
import yaml


ROOT = Path(__file__).resolve().parents[1]
READMES = ("README.md", "README.es.md", "README.pt-BR.md")
START = "<!-- skills:start -->"
END = "<!-- skills:end -->"


class ValidationError(ValueError):
    """An actionable catalog or upstream validation failure."""


def catalog_entries(text):
    """Parse real Markdown list links, including reference links, inside markers."""
    tokens = MarkdownIt().parse(text)
    starts = [i for i, t in enumerate(tokens) if t.type == "html_block" and t.content.strip() == START]
    ends = [i for i, t in enumerate(tokens) if t.type == "html_block" and t.content.strip() == END]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValidationError("Expected one ordered pair of skills:start / skills:end markers")
    entries = []
    expect_entry = False
    for token in tokens[starts[0] + 1:ends[0]]:
        if token.type == "list_item_open":
            expect_entry = True
        elif token.type == "inline" and expect_entry:
            children = token.children or []
            if not children or children[0].type != "link_open":
                raise ValidationError("Every skill bullet must start with a linked skill name")
            label = []
            for child in children[1:]:
                if child.type == "link_close":
                    break
                label.append(child.content)
            entries.append(("".join(label), children[0].attrGet("href")))
            expect_entry = False
    if not entries:
        raise ValidationError("No skill entries found")
    if len({url for _, url in entries}) != len(entries):
        raise ValidationError("Duplicate skill source URLs in catalog")
    return entries


def matching_catalogs(documents):
    canonical = catalog_entries(documents[0])
    for name, text in zip(READMES[1:], documents[1:]):
        if Counter(catalog_entries(text)) != Counter(canonical):
            raise ValidationError(f"{name}: skill names and URLs must match README.md")
    return canonical


def check_skill(text):
    """Verify basic Agent Skills metadata and instructions, not their quality."""
    match = re.match(r"\A\ufeff?---\s*\n(.*?)\n---\s*\n(.*)\Z", text, re.S)
    if not match:
        raise ValidationError("SKILL.md must contain YAML frontmatter and instructions")
    try:
        metadata = yaml.safe_load(match[1])
    except yaml.YAMLError as exc:
        raise ValidationError("Invalid YAML frontmatter") from exc
    if not isinstance(metadata, dict):
        raise ValidationError("Skill frontmatter must be a YAML mapping")
    for field in ("name", "description"):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            raise ValidationError(f"Skill requires a nonempty string '{field}'")
    if not match[2].strip():
        raise ValidationError("SKILL.md has no instructions after its frontmatter")


@lru_cache(maxsize=256)
def github_api(path):
    """Only send the optional token to GitHub's API, never to catalog URLs."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "awesome-wp-skills-validator"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request("https://api.github.com" + path, headers=headers)
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            hint = " (check GitHub rate limits/token permissions)" if exc.code in (403, 429) else ""
            raise ValidationError(f"GitHub API returned HTTP {exc.code}{hint}: {path}") from exc
        except (URLError, TimeoutError) as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise ValidationError(f"GitHub API could not be reached: {path}") from exc


def skill_file(repo, ref, path, api):
    data = api(f"/repos/{repo}/contents/{quote(path, safe='/')}?ref={quote(ref, safe='')}")
    if not isinstance(data, dict) or data.get("type") != "file" or data.get("encoding") != "base64":
        raise ValidationError(f"Not a readable skill file: {path}")
    try:
        text = base64.b64decode(data["content"]).decode("utf-8")
    except (KeyError, ValueError, UnicodeError) as exc:
        raise ValidationError(f"Could not decode {path}") from exc
    check_skill(text)


def validate_source(url, api=github_api):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "github.com" or parsed.query or parsed.fragment:
        raise ValidationError("Use a canonical HTTPS GitHub skill file, directory, or repository URL")
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2 or not all(re.fullmatch(r"[A-Za-z0-9_.-]+", p) for p in parts[:2]):
        raise ValidationError("Invalid GitHub repository URL")
    repo = "/".join(parts[:2])
    if len(parts) == 2:
        ref = api(f"/repos/{repo}")["default_branch"]
        prefix = ""
    elif len(parts) >= 5 and parts[2] in ("blob", "tree"):
        ref = unquote(parts[3])
        path = unquote("/".join(parts[4:]))
        if parts[2] == "blob":
            if path.split("/")[-1] != "SKILL.md":
                raise ValidationError("Direct skill links must point to SKILL.md, not a README or other file")
            skill_file(repo, ref, path, api)
            return path
        prefix = path.rstrip("/") + "/"
    else:
        raise ValidationError("Link to SKILL.md, its directory, or the repository root")

    tree = api(f"/repos/{repo}/git/trees/{quote(ref, safe='')}?recursive=1")
    if tree.get("truncated"):
        raise ValidationError("Repository tree is truncated; link directly to SKILL.md instead")
    candidates = sorted(item["path"] for item in tree.get("tree", [])
                        if item.get("type") == "blob" and item["path"].startswith(prefix)
                        and item["path"].split("/")[-1] == "SKILL.md")
    if not candidates:
        raise ValidationError("No SKILL.md found at this source")
    # The collection must contain at least one actual skill, not just a file name.
    failures = []
    for path in candidates:
        try:
            skill_file(repo, ref, path, api)
            return path
        except ValidationError as exc:
            failures.append(f"{path}: {exc}")
    raise ValidationError("No valid skill found: " + "; ".join(failures))


def main():
    try:
        entries = matching_catalogs([(ROOT / name).read_text(encoding="utf-8") for name in READMES])
    except (OSError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    failures = 0
    for name, url in entries:
        try:
            path = validate_source(url)
            print(f"PASS: {name} -> {path}", flush=True)
        except (ValidationError, KeyError, json.JSONDecodeError) as exc:
            print(f"FAIL: {name} ({url}): {exc}", file=sys.stderr, flush=True)
            failures += 1
    print(f"Checked {len(entries)} unique skill sources across {len(READMES)} editions; {failures} failed.")
    return int(failures > 0)


if __name__ == "__main__":
    sys.exit(main())
