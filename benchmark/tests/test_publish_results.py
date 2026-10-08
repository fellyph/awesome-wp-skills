import json
import tempfile
import unittest
from pathlib import Path

from benchmark.publish_results import publish_round


class PublishResultsTests(unittest.TestCase):
    def test_exports_only_submitted_public_artifacts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run = root / "raw" / "runs" / "0000-test"
            (run / "project").mkdir(parents=True)
            (run / "evaluation").mkdir()
            (run / "project" / "theme.json").write_text("{}")
            (run / "evaluation" / "theme.zip").write_bytes(b"theme")
            (run / "evaluation" / "request.json").write_text('{"reference":"hidden"}')
            result = {"model":"test-model", "skill":None, "task":"test", "category":"themes", "profile":"wordpress-project-v2", "scoring_version":"v1", "artifact_pass":True, "execution_completion":True, "delivery_success":True, "status":"passed", "score":100, "known_cost_usd":1, "cost_complete":True, "tokens":10, "calls":1, "generation_seconds":1, "evaluation_seconds":1, "development_iterations":1, "generation_status":"completed", "cost_basis":[], "visual_review":{}, "task_version":"1", "evaluation":{"checks":{"activation":True}}}
            (run / "result.json").write_text(json.dumps(result))
            (run / "agent.json").write_text(json.dumps({"error":"not used"}))
            target = publish_round(root / "raw", root / "published")
            self.assertTrue((target / "no-skill" / "source" / "theme.json").exists())
            self.assertTrue((target / "no-skill" / "theme.zip").exists())
            self.assertFalse((target / "no-skill" / "request.json").exists())
            self.assertNotIn("hidden", (target / "index.json").read_text())

    def test_does_not_attribute_starter_evaluation_to_a_model(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run = root / "raw" / "runs" / "0000-test"
            run.mkdir(parents=True)
            result = {"model":"test-model", "skill":None, "calls":0, "score":20, "artifact_pass":False,
                      "execution_completion":False, "delivery_success":False, "status":"token_preflight_error",
                      "known_cost_usd":0, "tokens":0, "evaluation": {"checks": {"cta": False}}}
            (run / "result.json").write_text(json.dumps(result))
            (run / "agent.json").write_text(json.dumps({"error":"preflight failed"}))
            target = publish_round(root / "raw", root / "published")
            exported = json.loads((target / "no-skill" / "result.json").read_text())
            self.assertIsNone(exported["score"])
            self.assertIsNone(exported["artifact_pass"])
            self.assertEqual(exported["checks"], {})

    def test_rounds_float_cost_and_links_navigation_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run = root / "raw" / "runs" / "0000-test"
            (run / "project").mkdir(parents=True)
            (run / "evaluation").mkdir()
            (run / "project" / "theme.json").write_text("{}")
            (run / "navigation-audit-v2.json").write_text('{"audit":"navigation-observation-v2"}')
            result = {"model":"test-model", "skill":None, "task":"test", "category":"themes",
                      "profile":"wordpress-project-v2", "scoring_version":"v1", "artifact_pass":True,
                      "execution_completion":True, "delivery_success":True, "status":"passed",
                      "score":100, "known_cost_usd":2.7879519999999993, "cost_complete":True,
                      "tokens":10, "calls":1, "evaluation":{"checks":{"activation":True}}}
            (run / "result.json").write_text(json.dumps(result))
            (run / "agent.json").write_text(json.dumps({}))
            target = publish_round(root / "raw", root / "published")
            exported = json.loads((target / "no-skill" / "result.json").read_text())
            self.assertEqual(exported["known_cost_usd"], 2.787952)
            readme = (target / "README.md").read_text()
            self.assertIn("$2.787952", readme)
            self.assertNotIn("2.7879519999999993", readme)
            self.assertIn("no-skill/navigation-audit-v2.json", readme)

    def test_exports_files_only_diagnostic_round(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run = root / "raw" / "runs" / "0000-test"
            (run / "project").mkdir(parents=True)
            (run / "evaluation").mkdir()
            (run / "project" / "fixture.php").write_text("<?php\n")
            (run / "evaluation" / "evidence.json").write_text('{"checks":{"renders":true}}')
            (run / "evaluation" / "screenshot.png").write_bytes(b"png")
            result = {
                "model": "gemini-3.8-flash",
                "skill": "frontend-design",
                "task": "accessibility-form",
                "category": "accessibility",
                "environment": {"tool_profile": "files-only-v1"},
                "generation_status": "budget_exceeded",
                "status": "budget_exceeded",
                "success": False,
                "score": 100.0,
                "known_cost_usd": 0.12794025,
                "cost_complete": True,
                "tokens": 66067,
                "calls": 5,
                "evaluation": {"score": 100.0, "success": True, "checks": {"renders": True}},
            }
            (run / "result.json").write_text(json.dumps(result))
            (run / "agent.json").write_text(json.dumps({}))
            target = publish_round(root / "raw", root / "published")
            exported = json.loads((target / "frontend-design" / "result.json").read_text())
            self.assertEqual(exported["profile"], "files-only-v1")
            self.assertEqual(exported["scoring_version"], "micro-v1")
            self.assertTrue(exported["artifact_pass"])
            self.assertFalse(exported["execution_completion"])
            self.assertFalse(exported["delivery_success"])
            self.assertEqual(exported["known_cost_usd"], 0.12794)
            self.assertTrue((target / "frontend-design" / "screenshot.png").exists())
            readme = (target / "README.md").read_text()
            self.assertIn("frontend-design/evidence.json", readme)
            self.assertIn("frontend-design/screenshot.png", readme)
            self.assertNotIn("theme.zip", readme)
