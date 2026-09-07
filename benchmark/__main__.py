"""Command-line interface: python -m benchmark --help."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from benchmark.core import ROOT, CATEGORIES, atomic_json, load_round, load_tasks, matrix, read_json
from benchmark.environments import evaluate
from benchmark.reporting import report
from benchmark.runner import run
from benchmark.skills import sync


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('sync-skills', help='Download resources pinned in skills.lock.json')
    validate = sub.add_parser('validate', help='Validate tasks, blueprints and a round without model calls')
    validate.add_argument('--config', type=Path, default=ROOT / 'configs/smoke.json')
    plan = sub.add_parser('plan', help='Print the matrix without starting any executions')
    plan.add_argument('--config', type=Path, default=ROOT / 'configs/pilot.json')
    execute = sub.add_parser('run', help='Execute or resume the exact configured round')
    execute.add_argument('--config', required=True, type=Path)
    execute.add_argument('--output', required=True, type=Path)
    execute.add_argument('--live', action='store_true', help='Explicitly enable billable model calls')
    results = sub.add_parser('report', help='Regenerate Markdown, JSON and CSV summaries')
    results.add_argument('directory', type=Path)
    fixtures = sub.add_parser('verify-fixtures', help='Evaluate known good and bad solutions in Playground')
    fixtures.add_argument('--category', choices=sorted(CATEGORIES))
    fixtures.add_argument('--output', type=Path, default=ROOT.parent / 'results/fixtures')
    prepare = sub.add_parser('prepare-live', help='Build a live pilot config from a reviewed model list')
    prepare.add_argument('--category', choices=['all'] + sorted(CATEGORIES), default='all')
    prepare.add_argument('--models', required=True, type=Path)
    prepare.add_argument('--budget', required=True, type=float)
    prepare.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    if args.command == 'sync-skills':
        sync()
    elif args.command in ('plan', 'validate'):
        config = load_round(args.config)
        if args.command == 'validate':
            subprocess.run(['node', str(ROOT / 'environments/validate.mjs')], check=True)
        runs = matrix(config)
        print(json.dumps({'runs': len(runs), 'categories': sorted({r['category'] for r in runs}),
                          'models': [m['id'] for m in config['models']],
                          'max_round_usd': config['limits']['max_round_usd'],
                          'matrix': runs if args.command == 'plan' else None}, indent=2))
    elif args.command == 'prepare-live':
        config = read_json(ROOT / 'configs' / ('full.json' if args.category == 'all' else args.category + '.json'))
        config['models'] = read_json(args.models)
        if any(m.get('adapter') in (None, 'mock') for m in config['models']):
            raise ValueError('Live model list must contain native or openrouter models')
        config['limits']['max_round_usd'] = args.budget
        atomic_json(args.output, config)
        load_round(args.output)
        print(f'Prepared {args.output}. Review the plan before running with --live.')
    elif args.command == 'run':
        config = load_round(args.config)
        if any(m['adapter'] != 'mock' for m in config['models']) and not args.live:
            raise ValueError('This round makes paid calls. Specify --live to enable it.')
        try:
            run(args.config, args.output)
        finally:
            if (args.output / 'manifest.json').exists():
                report(args.output)
        status = read_json(args.output / 'round-status.json')['status']
        if status != 'completed':
            return 2
    elif args.command == 'report':
        report(args.directory)
    elif args.command == 'verify-fixtures':
        results = []
        for task in load_tasks().values():
            if args.category and task['category'] != args.category:
                continue
            for variant in ('initial', 'reference'):
                directory = args.output / task['id'] / variant
                result = evaluate(task, task[variant], directory)
                expected = variant == 'reference'
                correct = result['status'] != 'infrastructure_error' and result['success'] == expected
                results.append({'task': task['id'], 'variant': variant, 'expected_success': expected,
                                'valid_evaluator': correct, 'result': result})
                atomic_json(args.output / 'fixtures.json', results)
                print(f'{task["id"]}/{variant}: {"OK" if correct else "ERROR"} {result}', flush=True)
        if not all(r['valid_evaluator'] for r in results):
            return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'benchmark: {error}', file=sys.stderr)
        sys.exit(1)
