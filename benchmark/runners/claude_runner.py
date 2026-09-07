"""Runner implementation for Claude Code CLI."""

import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional

from benchmark.config import CLAUDE_BIN, SKILLS_DIR
from benchmark.runners.base import BaseRunner


class ClaudeRunner(BaseRunner):
    """Executes benchmarks using Claude Code CLI."""

    def __init__(
        self,
        executable_path: str = CLAUDE_BIN,
        timeout_seconds: int = 300,
        model: Optional[str] = None,
        extra_flags: Optional[List[str]] = None
    ):
        super().__init__(
            name='claude',
            executable_path=executable_path,
            timeout_seconds=timeout_seconds,
            model=model,
            extra_flags=extra_flags
        )

    def mount_skill(self, workspace_dir: Path, skill_name: str) -> None:
        """Mount skill into .claude/skills/<skill_name>."""
        src_skill = SKILLS_DIR / skill_name
        if not src_skill.exists():
            return
        dest_skill_dir = workspace_dir / '.claude' / 'skills' / skill_name
        dest_skill_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_skill, dest_skill_dir, dirs_exist_ok=True)

    def build_command(self, prompt: str, workspace_dir: Path) -> List[str]:
        cmd = [
            self.executable_path,
            '-p', prompt,
            '--allow-dangerously-skip-permissions',
            '--output-format', 'json'
        ]
        if self.model:
            cmd.extend(['--model', self.model])
        if self.extra_flags:
            cmd.extend(self.extra_flags)
        return cmd

    def parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        result = {'raw': stdout, 'tokens': None}
        if not stdout.strip():
            return result

        try:
            data = json.loads(stdout)
            result['raw'] = data
            usage = data.get('usage') or data.get('token_usage') or {}
            result['tokens'] = {
                'prompt_tokens': usage.get('input_tokens') or usage.get('prompt_tokens'),
                'completion_tokens': usage.get('output_tokens') or usage.get('completion_tokens'),
                'total_tokens': usage.get('total_tokens')
            }
        except json.JSONDecodeError:
            pass

        return result
