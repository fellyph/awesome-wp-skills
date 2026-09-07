"""Paired, per-task comparisons; never mix simulated and measured results."""
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from benchmark.core import atomic_json, read_json


def mean(values):
    values = list(values)
    return statistics.mean(values) if values else None


def report(directory):
    directory = Path(directory)
    manifest = read_json(directory / 'manifest.json')
    rows = [read_json(p) for p in sorted((directory / 'runs').glob('*/result.json'))]
    groups = defaultdict(list)
    baselines = {}
    for row in rows:
        groups[(row['category'], row['task'], row['model'], row['skill'] or 'none', row['simulated'])].append(row)
        if row['skill'] is None:
            baselines[(row['task'], row['model'], row['repetition'], row['simulated'])] = row
    summaries = []
    for (category, task, model, skill, simulated), items in sorted(groups.items()):
        valid = [r for r in items if r['evaluation']['status'] != 'infrastructure_error' and r.get('generation_status') not in ('provider_error', 'usage_unavailable')]
        scored = [r['score'] for r in valid if r['score'] is not None]
        costs = [r['cost_usd'] for r in items]
        all_costs_known = all(c is not None for c in costs)
        pairs = []
        for row in valid:
            base = baselines.get((task, model, row['repetition'], simulated))
            if base and base['evaluation']['status'] != 'infrastructure_error' and base.get('generation_status') not in ('provider_error', 'usage_unavailable'):
                pairs.append((row, base))
        def delta(field):
            return mean(r[field] - b[field] for r,b in pairs if r[field] is not None and b[field] is not None)
        successes = sum(r['success'] for r in valid)
        summaries.append({'category': category, 'task': task, 'model': model, 'skill': skill,
                          'simulated': simulated, 'cost_basis': sorted({b for r in items for b in r.get('cost_basis', [])}), 'attempts': len(items), 'evaluated': len(valid),
                          'infrastructure_errors': len(items)-len(valid), 'success_rate': successes/len(valid) if valid else None,
                          'score_mean': mean(scored), 'score_stdev': statistics.stdev(scored) if len(scored)>1 else None,
                          'cost_mean_usd': mean(costs) if all_costs_known else None,
                          'cost_per_success_usd': sum(costs)/successes if all_costs_known and successes else None,
                          'generation_seconds_mean': mean(r['generation_seconds'] for r in items if r['generation_seconds'] is not None),
                          'paired_repetitions': len(pairs), 'score_delta': delta('score'),
                          'cost_delta_usd': delta('cost_usd'), 'seconds_delta': delta('generation_seconds')})
    categories = category_summaries(manifest, summaries)
    pending = [str(p.parent.relative_to(directory)) for p in (directory / 'runs').glob('*/progress.json') if not (p.parent / 'result.json').exists()]
    atomic_json(directory / 'category-summary.json', categories)
    atomic_json(directory / 'summary.json', {'identity': manifest['identity'], 'expected_runs': len(manifest['runs']),
                                            'completed_runs': len(rows), 'pending_runs': pending, 'groups': summaries})
    fields = list(summaries[0]) if summaries else ['category', 'task', 'model', 'skill']
    with (directory / 'summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(summaries)
    fmt = lambda value: 'N/A' if value is None else f'{value:.3f}'
    lines = ['# Benchmark results', '', f'Completed: {len(rows)} / {len(manifest["runs"])} planned executions.', '',
             'Simulated rows validate the harness only. They are not evidence of model or skill quality.', '',
             'Runtime: WordPress Playground (PHP WASM / SQLite). Results are not production hosting measurements.', '',
             '| Category / task | Model | Skill | Simulated | Evaluated | Success | Score ± SD | USD / success | Δ score vs no skill |',
             '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for s in summaries:
        clean = lambda v: str(v).replace('|','\\|').replace('\n',' ')
        lines.append('| ' + ' | '.join(map(clean, [s['category']+'/'+s['task'],s['model'],s['skill'],s['simulated'],s['evaluated'],fmt(s['success_rate']),fmt(s['score_mean'])+' ± '+fmt(s['score_stdev']),fmt(s['cost_per_success_usd']),fmt(s['score_delta'])])) + ' |')
    lines += ['', 'Category comparisons on shared tasks are in category-summary.json. Pending or interrupted runs: ' + str(len(pending)) + '.', '', 'Comparisons are paired by task, model and repetition. Compare skills only on shared tasks.', '',
              'Infrastructure/provider errors are excluded from quality denominators and counted separately. Known costs of failed attempts remain included. Missing usage is N/A.', '',
              'See summary.json and summary.csv for cost/time differences and coverage. Source changes and evaluation evidence are under runs/.', '']
    (directory / 'report.md').write_text('\n'.join(lines))
    return summaries


def category_summaries(manifest, summaries):
    """Use manifest eligibility, not observed winners, to choose the common task set."""
    result = []
    for category in sorted({r['category'] for r in manifest['runs']}):
        for model in manifest['config']['models']:
            planned = [r for r in manifest['runs'] if r['category'] == category and r['model'] == model['id']]
            by_skill = defaultdict(set)
            for run in planned:
                by_skill[run['skill'] or 'none'].add(run['task'])
            if not by_skill:
                continue
            common = set.intersection(*by_skill.values())
            for skill, eligible in sorted(by_skill.items()):
                selected = [s for s in summaries if s['category'] == category and s['model'] == model['id'] and s['skill'] == skill and s['task'] in common]
                result.append({'category': category, 'model': model['id'], 'skill': skill,
                               'simulated': model['adapter'] == 'mock', 'common_tasks': sorted(common),
                               'eligible_tasks': sorted(eligible), 'observed_tasks': len(selected),
                               'expected_repetitions_per_task': manifest['config']['repetitions'],
                               'evaluated_repetitions': sum(s['evaluated'] for s in selected),
                               'score_mean_equal_task_weight': mean(s['score_mean'] for s in selected if s['score_mean'] is not None) if len(selected)==len(common) and common and all(s['score_mean'] is not None for s in selected) else None,
                               'score_delta_equal_task_weight': mean(s['score_delta'] for s in selected if s['score_delta'] is not None) if len(selected)==len(common) and common and all(s['score_delta'] is not None for s in selected) else None})
    return result
