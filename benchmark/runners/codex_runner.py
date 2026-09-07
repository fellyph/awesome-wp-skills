"""Runner implementation for Codex CLI."""

import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional

from benchmark.config import CODEX_BIN, SKILLS_DIR
from benchmark.runners.base import BaseRunner


class CodexRunner(BaseRunner):
    """Executes benchmarks using OpenAI Codex CLI."""

    def __init__(
        self,
        executable_path: str = CODEX_BIN,
        timeout_seconds: int = 300,
        model: Optional[str] = None,
        extra_flags: Optional[List[str]] = None
    ):
        super().__init__(
            name='codex',
            executable_path=executable_path,
            timeout_seconds=timeout_seconds,
            model=model,
            extra_flags=extra_flags
        )

    def mount_skill(self, workspace_dir: Path, skill_name: str) -> None:
        """Mount skill into workspace AGENTS.md and .agents/skills/."""
        src_skill = SKILLS_DIR / skill_name
        if not src_skill.exists():
            return

        # 1. Provide in .agents/skills for tools looking there
        dest_skill_dir = workspace_dir / '.agents' / 'skills' / skill_name
        dest_skill_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src_skill, dest_skill_dir, dirs_exist_ok=True)

        # 2. Append skill markdown to AGENTS.md for Codex workspace instructions
        skill_md = src_skill / 'SKILL.md'
        if skill_md.exists():
            agents_md = workspace_dir / 'AGENTS.md'
            content = f'

# Skill: {skill_name}
' + skill_md.read_text(encoding='utf-8')
            with open(agents_md, 'a', encoding='utf-8') as f:
                f.write(content)

    def build_command(self, prompt: str, workspace_dir: Path) -> List[str]:
        cmd = [
            self.executable_path,
            'exec',
            prompt,
            '--json'
        ]
        if self.model:
            cmd.extend(['-c', f'model="{self.model}"'])
        if self.extra_flags:
            cmd.extend(self.extra_flags)
        return cmd

    def parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        result = {'raw': stdout, 'tokens': None}
        if not stdout.strip():
            return result

        # Parse JSONL lines
        events = []
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0

        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                events.append(event)
                # Look for token usage events
                if 'usage' in event and isinstance(event['usage'], dict):
                    u = event['usage']
                    prompt_tokens = u.get('prompt_tokens', 0)
                    completion_tokens = u.get('completion_tokens', 0)
                    total_tokens = u.get('total_tokens', 0)
            except json.JSONDecodeError:
                pass

        result['events'] = events
        if total_tokens > 0:
            result['tokens'] = {
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            }

        return result
