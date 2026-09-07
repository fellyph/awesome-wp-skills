"""Portable paths for the benchmark; execution settings live in round JSON files."""
from pathlib import Path

BENCHMARK_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BENCHMARK_DIR.parent
TASKS_DIR = BENCHMARK_DIR / 'tasks'
SKILLS_DIR = BENCHMARK_DIR / '.cache' / 'skills'
RESULTS_DIR = PROJECT_ROOT / 'results'
DEFAULT_CONFIG = BENCHMARK_DIR / 'configs' / 'smoke.json'
