"""Versioned manifests and deterministic, individually applied skill conditions."""
import hashlib
import json
import math
import random
from pathlib import Path
from datetime import date
from benchmark.adapters.providers import PROVIDERS, PARAMETERS

ROOT = Path(__file__).resolve().parent
CATEGORIES = {"themes", "plugins", "fixes", "performance", "accessibility"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def files(path):
    """Read only regular UTF-8 resources, never follow a link outside a snapshot."""
    path = Path(path).resolve()
    result = {}
    for item in sorted(path.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"Symlink is not allowed: {item}")
        if item.is_file():
            result[item.relative_to(path).as_posix()] = item.read_text()
    return result


def positive(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be finite and positive")


def load_tasks():
    result = {}
    for path in sorted((ROOT / "tasks").glob("*/task.json")):
        task = read_json(path)
        if task["id"] != path.parent.name or task["category"] not in CATEGORIES:
            raise ValueError(f"Invalid task: {path}")
        task.setdefault("profile", "files-only-v1")
        task.setdefault("scoring_version", "micro-v1")
        task.setdefault("version", "1.0.0")
        if task["profile"] == "wordpress-project-v2":
            materials = read_json(path.parent / 'materials.json')
            for name, expected_hash in materials['sha256'].items():
                if hashlib.sha256((path.parent / name).read_bytes()).hexdigest() != expected_hash:
                    raise ValueError('Frozen scenario material changed: ' + name)
            task['materials_hash'] = digest(materials)
            task["public_hashes"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((path.parent / "public").glob("*")) if p.is_file()}
            task["fixtures_hash"] = digest(files(path.parent / "fixtures"))
        task["prompt"] = (path.parent / "prompt.txt").read_text()
        task["initial"] = files(path.parent / "initial")
        task["reference"] = files(path.parent / "reference")
        task["evaluator"] = (path.parent / "evaluate.php").read_text()
        task["blueprint"] = read_json(path.parent / "blueprint.json")
        checks = task["checks"]
        if not checks or len({c["id"] for c in checks}) != len(checks):
            raise ValueError(f"Duplicate/empty checks: {task['id']}")
        if not any(c.get("critical") for c in checks):
            raise ValueError("At least one critical acceptance criterion is required")
        for check in checks:
            positive(check["weight"], "check weight")
            if not isinstance(check["critical"], bool):
                raise ValueError("critical must be boolean")
        task["hash"] = digest(task)
        result[task["id"]] = task
    if not result:
        raise ValueError("No tasks found")
    return result


def load_round(path):
    config = read_json(path)
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported round schema")
    if not isinstance(config["repetitions"], int) or isinstance(config["repetitions"], bool) or config["repetitions"] < 1:
        raise ValueError("repetitions must be a positive integer")
    if not isinstance(config["seed"], int):
        raise ValueError("seed must be an integer")
    for field in ("timeout_seconds", "max_calls", "max_output_tokens", "max_total_tokens", "max_run_usd", "max_round_usd", "max_model_usd"):
        positive(config["limits"][field], field)
    if config["limits"]["max_model_usd"] > 20:
        raise ValueError("The approved per-model budget is at most USD 20")
    for field in ("max_calls", "max_output_tokens", "max_total_tokens"):
        if not isinstance(config["limits"][field], int):
            raise ValueError(f"{field} must be an integer")
    tasks = load_tasks()
    if not config["tasks"] or len(set(config["tasks"])) != len(config["tasks"]):
        raise ValueError("Round tasks must be nonempty and unique")
    if set(config["tasks"]) - tasks.keys():
        raise ValueError("Unknown task")
    if config["limits"]["max_run_usd"] > config["limits"]["max_model_usd"]:
        raise ValueError("Per-run budget must not exceed the per-model budget")
    models = config["models"]
    if not models or len({m["id"] for m in models}) != len(models):
        raise ValueError("Model IDs must be unique")
    for model in models:
        allowed = {"id", "adapter", "behavior", "provider", "parameters", "pricing", "budget_group"}
        if set(model) - allowed:
            raise ValueError("Unknown model fields; credentials must use environment variables")
        if not isinstance(model["id"], str) or not model["id"].strip():
            raise ValueError("Model ID must be a nonempty string")
        if "budget_group" in model and (not isinstance(model["budget_group"], str) or not model["budget_group"].strip()):
            raise ValueError("budget_group must be a nonempty string")
        if model["adapter"] not in ({"mock"} | PROVIDERS.keys()):
            raise ValueError("Unsupported adapter")
        if model["adapter"] == "mock" and model.get("behavior") not in ("reference", "initial"):
            raise ValueError("Mock behavior must be reference or initial")
        if model["adapter"] != "mock":
            if (model["adapter"] == "openrouter" and not model.get("provider")) or not isinstance(model.get("parameters"), dict):
                raise ValueError("Live models need pinned provider and parameters")
            if "REPLACE" in model["id"] or (model.get("provider") and "REPLACE" in model["provider"]):
                raise ValueError("Replace example model/provider identifiers before running")
            pricing = model.get("pricing", {})
            for key in ("input_per_million_usd", "output_per_million_usd"):
                positive(pricing.get(key), key)
            if not pricing.get("source_url", "").startswith("https://") or not pricing.get("checked_on"):
                raise ValueError("Live models require dated pricing evidence")
            date.fromisoformat(pricing["checked_on"])
            for key in ("cached_input_per_million_usd", "cache_write_per_million_usd"):
                if key in pricing:
                    positive(pricing[key], key)
            if set(model["parameters"]) - PARAMETERS[model["adapter"]]:
                raise ValueError("Unsupported model parameter")
            if model['adapter'] == 'openai' and model['id'].startswith('gpt-6-astra'):
                if {'temperature', 'top_p'} & model['parameters'].keys():
                    raise ValueError('GPT-6 Astra does not support temperature or top_p')
                if model['parameters'].get('reasoning_effort', 'medium') not in ('low', 'medium', 'high', 'xhigh', 'max'):
                    raise ValueError('Unsupported GPT-6 Astra reasoning effort')
    profiles = {tasks[t]["profile"] for t in config["tasks"]}
    if len(profiles) != 1:
        raise ValueError("Execution profiles must be run and scored in separate rounds")
    if "wordpress-project-v2" in profiles and any(m["adapter"] not in ("gemini", "openai", "anthropic", "mock") for m in models):
        raise ValueError("wordpress-project-v2 requires a supported multimodal adapter (Gemini, OpenAI or Anthropic)")
    locks = read_json(ROOT / "skills.lock.json")
    skills = {}
    for skill_id in config["skills"]:
        if skill_id in skills or skill_id not in locks:
            raise ValueError(f"Duplicate or unknown skill: {skill_id}")
        lock = locks[skill_id]
        resource = files(ROOT / lock["path"])
        if digest(resource) != lock["sha256"]:
            raise ValueError(f"Skill snapshot changed: {skill_id}; update lock explicitly")
        if "SKILL.md" not in resource or not lock["source"] or not lock["revision"]:
            raise ValueError(f"Incomplete skill provenance: {skill_id}")
        skills[skill_id] = {**lock, "files": resource}
    config["resolved_tasks"] = {k: tasks[k] for k in config["tasks"]}
    config["resolved_skills"] = skills
    return config


def matrix(config):
    runs = []
    for task_id, task in config["resolved_tasks"].items():
        conditions = [None] + [s for s, metadata in config["resolved_skills"].items()
                               if task_id in metadata["tasks"]]
        for model in config["models"]:
            for repetition in range(config["repetitions"]):
                for skill in conditions:
                    runs.append({"task": task_id, "category": task["category"], "model": model["id"],
                                 "skill": skill, "repetition": repetition})
    random.Random(config["seed"]).shuffle(runs)
    return runs


def score(task, evidence):
    expected = {c["id"] for c in task["checks"]}
    actual = evidence.get("checks", {})
    if set(actual) != expected or any(type(value) is not bool for value in actual.values()):
        raise ValueError("Evaluator evidence does not match the task rubric")
    total = sum(c["weight"] for c in task["checks"])
    points = sum(c["weight"] for c in task["checks"] if actual[c["id"]])
    return {"score": round(100 * points / total, 2),
            "success": all(actual[c["id"]] for c in task["checks"] if c["critical"]),
            "checks": actual, "measurements": evidence.get("measurements", {})}
