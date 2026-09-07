"""Base runner interface and data models for benchmark executions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any, Dict, List, Optional

from benchmark.config import SKILLS_DIR, DEFAULT_TIMEOUT_SECONDS


@dataclass
class TokenUsage:
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> 'TokenUsage':
        if not data:
            return cls()
        return cls(
            prompt_tokens=data.get('prompt_tokens') or data.get('input_tokens'),
            completion_tokens=data.get('completion_tokens') or data.get('output_tokens'),
            total_tokens=data.get('total_tokens')
        )


@dataclass
class RunResult:
    task_id: str
    runner_name: str
    condition: str  # 'with_skill' or 'without_skill'
    prompt: str
    duration_seconds: float
    exit_code: int
    output_dir: str
    stdout: str
    stderr: str
    timestamp: str
    tokens: TokenUsage = field(default_factory=TokenUsage)
    error: Optional[str] = None
    raw_response: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


class BaseRunner(ABC):
    """Abstract base runner for agent CLIs."""

    def __init__(
        self,
        name: str,
        executable_path: str,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        model: Optional[str] = None,
        extra_flags: Optional[List[str]] = None
    ):
        self.name = name
        self.executable_path = executable_path
        self.timeout_seconds = timeout_seconds
        self.model = model
        self.extra_flags = extra_flags or []

    def is_available(self) -> bool:
        """Check if the runner executable exists on the system."""
        if not self.executable_path:
            return False
        path = Path(self.executable_path)
        return path.is_file() and os.access(path, os.X_OK)

    def prepare_workspace(self, task_spec: Dict[str, Any], with_skill: bool) -> Path:
        """Create an isolated temporary workspace for the run."""
        task_id = task_spec.get('id', 'unknown')
        condition = 'with_skill' if with_skill else 'without_skill'
        temp_dir = Path(tempfile.mkdtemp(prefix=f'bench_{task_id}_{condition}_'))

        # Copy any task fixture input files
        task_dir = task_spec.get('_task_dir')
        if task_dir:
            task_path = Path(task_dir)
            fixtures_dir = task_path / 'fixtures'
            if fixtures_dir.exists() and fixtures_dir.is_dir():
                for item in fixtures_dir.iterdir():
                    dest = temp_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)

        # Mount skill if requested
        if with_skill:
            skills = task_spec.get('skills', [])
            for skill_name in skills:
                self.mount_skill(temp_dir, skill_name)

        return temp_dir

    @abstractmethod
    def mount_skill(self, workspace_dir: Path, skill_name: str) -> None:
        """Mount or inject a skill into the runner workspace."""
        pass

    @abstractmethod
    def build_command(self, prompt: str, workspace_dir: Path) -> List[str]:
        """Construct command line arguments for the runner invocation."""
        pass

    @abstractmethod
    def parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse CLI output to extract tokens and structured response if available."""
        pass

    def run(
        self,
        task_spec: Dict[str, Any],
        with_skill: bool,
        output_dir: Path
    ) -> RunResult:
        """Execute a single benchmark run in an isolated environment."""
        task_id = task_spec.get('id', 'task')
        prompt = task_spec.get('prompt', '')
        condition = 'with_skill' if with_skill else 'without_skill'
        timestamp = datetime.now(timezone.utc).isoformat()

        workspace_dir = self.prepare_workspace(task_spec, with_skill)
        output_dir.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        exit_code = 0
        stdout = ''
        stderr = ''
        error_msg = None
        parsed: Dict[str, Any] = {}

        try:
            cmd = self.build_command(prompt, workspace_dir)
            import subprocess
            proc = subprocess.run(
                cmd,
                cwd=str(workspace_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            exit_code = proc.returncode
            stdout = proc.stdout
            stderr = proc.stderr
            parsed = self.parse_output(stdout, stderr)
        except subprocess.TimeoutExpired as te:
            exit_code = 124
            error_msg = f'Execution timed out after {self.timeout_seconds} seconds.'
            stdout = te.stdout or ''
            stderr = te.stderr or ''
        except Exception as exc:
            exit_code = 1
            error_msg = str(exc)

        duration = time.time() - start_time

        # Copy generated files from workspace to output_dir
        for item in workspace_dir.iterdir():
            # Exclude runner hidden configuration folders from final artifact directory
            if item.name in ('.agents', '.claude', '.gemini', '.git'):
                continue
            dest = output_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

        # Cleanup temporary workspace
        shutil.rmtree(workspace_dir, ignore_errors=True)

        token_usage = TokenUsage.from_dict(parsed.get('tokens'))

        return RunResult(
            task_id=task_id,
            runner_name=self.name,
            condition=condition,
            prompt=prompt,
            duration_seconds=round(duration, 2),
            exit_code=exit_code,
            output_dir=str(output_dir),
            stdout=stdout,
            stderr=stderr,
            timestamp=timestamp,
            tokens=token_usage,
            error=error_msg,
            raw_response=parsed.get('raw')
        )
