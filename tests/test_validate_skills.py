"""Regression checks for catalog parsing and rejecting misleading skill links."""

import base64
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_skills import (  # noqa: E402
    END, START, ValidationError, catalog_entries, check_skill,
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


if __name__ == "__main__":
    unittest.main()
