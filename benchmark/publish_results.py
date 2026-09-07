"""Publish a safe, tracked snapshot from one ignored benchmark round.

Raw rounds contain the hidden reference implementation in their manifest. This
export deliberately copies only submitted artifacts and public result evidence.
"""
import argparse
import json
import re
import shutil
from pathlib import Path


PUBLIC_EVALUATION_FILES = (
    "screenshot-desktop.png", "screenshot-mobile.png", "editor-saved.png",
    "editor-reloaded.png", "handover-published.png", "form-submitted.png",
    "theme.zip", "playground-bundle.zip", "evidence.json",
)
PUBLIC_RUN_FILES = ("navigation-audit-v2.json",)
RESULT_FIELDS = (
    "model", "skill", "task", "category", "profile", "scoring_version",
    "artifact_pass", "execution_completion", "delivery_success", "status",
    "score", "known_cost_usd", "cost_complete", "tokens", "calls",
    "generation_seconds", "evaluation_seconds", "development_iterations",
    "generation_status", "cost_basis", "visual_review", "task_version",
)


def read_json(path):
    return json.loads(Path(path).read_text())


def safe_result(result, agent):
    exported = {key: result.get(key) for key in RESULT_FIELDS}
    exported["checks"] = result.get("evaluation", {}).get("checks", {})
    exported["generated_artifact"] = result.get("calls", 0) > 0
    if not exported["generated_artifact"]:
        # Evaluation of the unchanged starter scaffold is not a model result.
        exported["score"] = None
        exported["artifact_pass"] = None
        exported["checks"] = {}
        exported["generation_error"] = agent.get("error") or result.get("generation_status")
    return exported


def publish_round(source, destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    run_paths = sorted(source.glob("runs/*/result.json"))
    if not run_paths:
        raise ValueError("No completed result records were found")
    rows = [(read_json(path), path.parent, read_json(path.parent / "agent.json")) for path in run_paths]
    models = {row[0]["model"] for row in rows}
    if len(models) != 1:
        raise ValueError("A published round must contain exactly one model")
    model = next(iter(models))
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", model):
        raise ValueError("Model ID cannot be used as a published path")
    target = destination / model / "latest"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    copied = []
    for result, run, agent in rows:
        condition = result["skill"] or "no-skill"
        folder = target / condition
        folder.mkdir()
        exported = safe_result(result, agent)
        (folder / "result.json").write_text(json.dumps(exported, indent=2) + "\n")
        if exported["generated_artifact"]:
            shutil.copytree(run / "project", folder / "source")
            evaluation = run / "evaluation"
            for name in PUBLIC_EVALUATION_FILES:
                if (evaluation / name).exists():
                    shutil.copy2(evaluation / name, folder / name)
            for name in PUBLIC_RUN_FILES:
                if (run / name).exists():
                    shutil.copy2(run / name, folder / name)
        copied.append((condition, exported))
    index = {
        "schema_version": 1,
        "model": model,
        "source_round": source.name,
        "conditions": [{"condition": condition, **result} for condition, result in copied],
        "retention": "latest tracked result per model; raw runs remain ignored",
    }
    (target / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    lines = [f"# Latest benchmark result: {model}", "", "This tracked snapshot contains only submitted artifacts and public evaluation evidence.",
             "The ignored raw round, its hidden reference source, request checkpoints and provider payloads are not included.", ""]
    for condition, result in copied:
        lines.extend([f"## {condition}", "", f"- Status: `{result['status']}`", f"- Automated score: `{result['score'] if result['generated_artifact'] else 'N/A — no model generation'}`", f"- Artifact pass: `{result['artifact_pass'] if result['generated_artifact'] else 'N/A — no model generation'}`", f"- Execution completion: `{result['execution_completion']}`", f"- Delivery success: `{result['delivery_success']}`", f"- Known cost: `${result['known_cost_usd']}`", f"- Tokens / calls: `{result['tokens']}` / `{result['calls']}`"])
        if result["generated_artifact"]:
            lines.extend([f"- [Source]({condition}/source/) · [theme ZIP]({condition}/theme.zip) · [Playground bundle]({condition}/playground-bundle.zip)",
                          f"- [Desktop screenshot]({condition}/screenshot-desktop.png) · [Mobile screenshot]({condition}/screenshot-mobile.png)"])
        else:
            lines.append(f"- No artifact was generated: `{result['generation_error']}`")
        lines.append("")
    (target / "README.md").write_text("\n".join(lines))
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Ignored round directory")
    parser.add_argument("--destination", type=Path, default=Path("benchmark/results"))
    args = parser.parse_args(argv)
    print(publish_round(args.source, args.destination))


if __name__ == "__main__":
    main()
