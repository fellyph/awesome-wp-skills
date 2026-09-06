"""Regression checks for catalog parsing and rejecting misleading skill links."""

import base64
import io
from pathlib import Path
import sys
import unittest
from unittest import mock
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_skills import (  # noqa: E402
    END, START, ValidationError, catalog_entries, check_skill, github_api,
    matching_catalogs, validate_source,
)

VALID = "---\nname: example\ndescription: A useful skill.\n---\n# Instructions\nDo the task.\n"
URL = "https://github.com/owner/repo/blob/main/skills/example/SKILL.md"


def document(bullet=f"- [Example]({URL})"):
    return f"{START}\n\n{bullet}\n\n{END}\n"


def file_response(content=VALID):
    return {"type": "file", "encoding": "base64",
            "content": base64.b64encode(content.encode()).decode()}


class CatalogTests(unittest.TestCase):
    def test_reference_link_and_mcp_exclusion(self):
        text = document("- [Example][skill]") + f"\n[skill]: {URL}\n\n- [MCP](https://example.org)\n"
        self.assertEqual(catalog_entries(text), [("Example", URL)])

    def test_code_blocks_cannot_create_entries_or_markers(self):
        with self.assertRaises(ValidationError):
            catalog_entries("```markdown\n" + document() + "```\n")
        text = document().replace(f"\n{END}", f"\n```md\n- [Fake](https://example.org)\n```\n\n{END}")
        self.assertEqual(len(catalog_entries(text)), 1)

    def test_missing_reversed_or_empty_markers(self):
        for text in ("- [Example](https://example.org)", f"{END}\n\n{START}", document("")):
            with self.subTest(text=text), self.assertRaises(ValidationError):
                catalog_entries(text)

    def test_unlinked_and_duplicate_entries_fail(self):
        for bullet in ("- Example without link", f"- [One]({URL})\n- [Two]({URL})"):
            with self.subTest(bullet=bullet), self.assertRaises(ValidationError):
                catalog_entries(document(bullet))

    def test_translation_source_drift_fails(self):
        self.assertEqual(len(matching_catalogs([document()] * 3)), 1)
        with self.assertRaises(ValidationError):
            matching_catalogs([document(), document().replace("owner/repo", "other/repo"), document()])

    def test_translation_links_outside_catalog_must_match(self):
        english = document() + "\n| [MCP](https://example.org/mcp) |\n\n![Badge](https://example.org/badge.svg)\n"
        translated = english.replace("https://example.org/mcp", "https://example.org/mcp-es")
        with self.assertRaisesRegex(ValidationError, "README.es.md.*mcp-es"):
            matching_catalogs([english, translated, english])
        # Heading anchors are translated, so they may differ between editions.
        self.assertEqual(len(matching_catalogs([english + "[a](#start-here)\n", english + "[a](#empieza-aqui)\n", english])), 1)

    def test_translation_commands_must_match(self):
        english = document() + "\n```sh\nnpx skills add owner/repo --skill example\n```\n"
        translated = english.replace("--skill example", "--skill exemplo")
        with self.assertRaisesRegex(ValidationError, "README.pt-BR.md: code examples"):
            matching_catalogs([english, english, translated])


class SourceTests(unittest.TestCase):
    def test_valid_direct_skill(self):
        paths = []
        def api(path):
            paths.append(path)
            return file_response()
        self.assertEqual(validate_source(URL, api), "skills/example/SKILL.md")
        self.assertEqual(paths, ["/repos/owner/repo/contents/skills/example/SKILL.md?ref=main"])

    def test_non_skill_links_fail_without_network(self):
        def no_network(path):
            self.fail(f"Should not request {path}")
        for url in (URL.replace("SKILL.md", "README.md"), "https://example.org/SKILL.md",
                    "https://github.com.evil.test/owner/repo", URL + "?raw=1"):
            with self.subTest(url=url), self.assertRaises(ValidationError):
                validate_source(url, no_network)

    def test_collection_finds_real_skill(self):
        def api(path):
            if path == "/repos/owner/repo":
                return {"default_branch": "main"}
            if "/git/trees/" in path:
                return {"tree": [{"type": "blob", "path": "skills/example/SKILL.md"}]}
            return file_response()
        self.assertEqual(validate_source("https://github.com/owner/repo", api), "skills/example/SKILL.md")

    def test_empty_or_truncated_collection_fails(self):
        for tree in ({"tree": []}, {"tree": [], "truncated": True}):
            def api(path):
                return {"default_branch": "main"} if path == "/repos/owner/repo" else tree
            with self.subTest(tree=tree), self.assertRaises(ValidationError):
                validate_source("https://github.com/owner/repo", api)

    def test_directory_cannot_use_skill_elsewhere(self):
        def api(path):
            return {"tree": [{"type": "blob", "path": "other/SKILL.md"}]}
        with self.assertRaises(ValidationError):
            validate_source("https://github.com/owner/repo/tree/main/empty", api)

    def test_skill_filename_alone_is_not_enough(self):
        with self.assertRaises(ValidationError):
            validate_source(URL, lambda path: file_response("# Just a README"))

    def test_metadata_and_instructions_required(self):
        check_skill(VALID)
        for text in ("# No frontmatter", "---\nname: example\n---\nBody",
                     "---\nname: []\ndescription: text\n---\nBody",
                     "---\nname: example\ndescription: [\n---\nBody",
                     "---\nname: example\ndescription: text\n---\n"):
            with self.subTest(text=text), self.assertRaises(ValidationError):
                check_skill(text)


class GitHubApiTests(unittest.TestCase):
    def setUp(self):
        github_api.cache_clear()

    def http_error(self, code):
        return HTTPError("https://api.github.com/x", code, "error", {}, None)

    def test_transient_errors_are_retried(self):
        responses = [self.http_error(503), io.BytesIO(b'{"ok": true}')]
        with mock.patch("validate_skills.urlopen", side_effect=responses) as urlopen, \
                mock.patch("validate_skills.time.sleep") as sleep:
            self.assertEqual(github_api("/repos/owner/repo"), {"ok": True})
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1)

    def test_client_errors_fail_immediately_with_a_hint(self):
        with mock.patch("validate_skills.urlopen", side_effect=self.http_error(403)) as urlopen, \
                mock.patch("validate_skills.time.sleep") as sleep:
            with self.assertRaisesRegex(ValidationError, "HTTP 403 .*rate limits"):
                github_api("/repos/owner/repo")
        self.assertEqual(urlopen.call_count, 1)
        sleep.assert_not_called()

    def test_token_is_only_sent_to_the_github_api(self):
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "secret"}), \
                mock.patch("validate_skills.urlopen", return_value=io.BytesIO(b"{}")) as urlopen:
            github_api("/repos/owner/repo")
        request = urlopen.call_args[0][0]
        self.assertEqual(request.full_url, "https://api.github.com/repos/owner/repo")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")


if __name__ == "__main__":
    unittest.main()
