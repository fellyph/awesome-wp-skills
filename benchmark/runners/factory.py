"""Runner registry and factory."""

from typing import Dict, List, Optional, Type

from benchmark.runners.base import BaseRunner
from benchmark.runners.agy_runner import AgyRunner
from benchmark.runners.claude_runner import ClaudeRunner
from benchmark.runners.codex_runner import CodexRunner

RUNNERS: Dict[str, Type[BaseRunner]] = {
    'agy': AgyRunner,
    'claude': ClaudeRunner,
    'codex': CodexRunner,
}


def get_runner(
    name: str,
    executable_path: Optional[str] = None,
    timeout_seconds: int = 300,
    model: Optional[str] = None,
    extra_flags: Optional[List[str]] = None
) -> BaseRunner:
    """Instantiate a benchmark runner by name."""
    normalized = name.lower().strip()
    if normalized not in RUNNERS:
        raise ValueError(
            f'Unknown runner "{name}". Supported runners: {list(RUNNERS.keys())}'
        )
    runner_cls = RUNNERS[normalized]
    kwargs = {
        'timeout_seconds': timeout_seconds,
        'model': model,
        'extra_flags': extra_flags
    }
    if executable_path:
        kwargs['executable_path'] = executable_path
    return runner_cls(**kwargs)


def list_runners() -> List[str]:
    """Return list of available runner names."""
    return sorted(RUNNERS.keys())
