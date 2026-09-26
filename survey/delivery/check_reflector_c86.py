"""CPU-only regression reproductions against a pinned reflector copy.

Never calls a model, network, live memory or live git repository. All writes and
git operations are restricted by fixture paths under a temporary directory.
Exit zero means the recorded observations reproduced, not production readiness.
"""
import contextlib
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
from types import SimpleNamespace

SOURCE = Path('/tmp/tern-reflector-c86/reflector-pinned.py')
RESULT = Path(__file__).with_name('c86-reflector-tests.json')
results = []


def git(mem, *args):
    return subprocess.run(['git', '-C', str(mem), *args], capture_output=True, text=True)


@contextlib.contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix='tern-reflector-test-') as name:
        root = Path(name)
        mem, skills, state = [root / s for s in ('memory', 'skills', 'state')]
        for p in (mem, skills, state):
            p.mkdir()
        (mem / 'MEMORY.md').write_text('# Memory\n')
        (mem / 'unrelated.md').write_text('original\n')
        git(mem, 'init', '-q')
        git(mem, 'config', 'user.name', 'Fixture')
        git(mem, 'config', 'user.email', 'fixture@invalid')
        git(mem, 'add', '.')
        assert git(mem, 'commit', '-qm', 'fixture').returncode == 0
        n = runpy.run_path(str(SOURCE), run_name='reflector_fixture')
        g = n['run'].__globals__
        g.update(MEM=str(mem), SKILLS=str(skills), STATE=str(state))
        g['signal'] = lambda _: (_ for _ in ()).throw(AssertionError('network forbidden'))
        g['ask_model'] = lambda _: (_ for _ in ()).throw(AssertionError('model forbidden'))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            yield g, root, mem, skills, state


def item(kind='feedback', slug='sample', quote='Use the blue option'):
    return dict(kind=kind, slug=slug, title='Fixture lesson', quote=quote,
                lesson='Fixture-only lesson', why='Fixture reason', how_to_apply='Fixture scope')


def run_fake(g, items):
    g['collect'] = lambda _: [{'ts': 1, 'brian': 'Use the blue option', 'before': 'fixture'}]
    g['ask_model'] = lambda _: (dict(items=items, corrections=1, repeats=0, summary='Fixture'), 0)
    return g['run'](SimpleNamespace(date='2026-09-26', dry_run=False, no_signal=True))


def record(name, observed, detail):
    assert observed, (name, detail)
    results.append(dict(test=name, reproduced=True, detail=detail))


with fixture() as (g, root, mem, skills, state):
    corpus = [{'brian': 'Use the blue option'}]
    a, _, r, _ = g['apply']([item(quote='Invented quote')], '2026-09-26', corpus, True)
    record('absent_quote_rejected', not a and len(r) == 1, 'Basic fabricated quote rejected.')
    a, _, r, _ = g['apply']([item(quote='alpha\nbeta')], '2026-09-26',
                           [{'brian': 'alpha'}, {'brian': 'beta'}], True)
    record('quote_crosses_message_boundary', len(a) == 1 and not r,
           'Joined corpus accepts a quote present in no individual user message.')

with fixture() as (g, root, mem, skills, state):
    projects = root / 'projects'
    for project, text in [('project-a', 'For project A use the blue option'),
                          ('project-b', 'For project B use the red option')]:
        d = projects / project; d.mkdir(parents=True)
        (d / 'session.jsonl').write_text(json.dumps(dict(type='user', cwd=project,
            timestamp='2026-09-26T12:00:00Z', message={'content': text})) + '\n')
    g['PROJECTS'] = str(projects)
    g['local_day_bounds'] = lambda _: (0, 9999999999)
    corpus = g['collect'](dt.date(2026, 9, 26))
    record('collector_drops_scope_and_source', len(corpus) == 2 and all(
        set(r) == {'ts', 'brian', 'before'} for r in corpus),
        'Different project sources are pooled without cwd, session or message identifiers.')

with fixture() as (g, root, mem, skills, state):
    (mem / 'unrelated.md').write_text('unrelated pending user edit\n')
    run_fake(g, [item()])
    names = git(mem, 'show', '--pretty=', '--name-only', 'HEAD').stdout.splitlines()
    record('whole_worktree_committed', 'unrelated.md' in names,
           'Reflector commit captured a pre-existing unrelated memory edit.')
    g['undo'](SimpleNamespace(date='2026-09-26'))
    record('undo_reverts_unrelated_edit', (mem / 'unrelated.md').read_text() == 'original\n',
           'Undo reverted the unrelated edit captured by git add -A.')

with fixture() as (g, root, mem, skills, state):
    run_fake(g, [item(kind='procedure', slug='skill-one')])
    run_fake(g, [])
    g['undo'](SimpleNamespace(date='2026-09-26'))
    record('same_date_manifest_loses_skill_undo', (skills / 'skill-one' / 'SKILL.md').exists(),
           'Second same-date run overwrote manifest; undo left first-run skill installed.')

with fixture() as (g, root, mem, skills, state):
    hook = mem / '.git/hooks/pre-commit'
    hook.write_text('#!/bin/sh\nexit 1\n'); hook.chmod(0o700)
    rc = run_fake(g, [item()])
    stat = json.loads((state / 'stats.jsonl').read_text())
    record('commit_rejection_reports_success', rc == 0 and stat['commit'] is None
           and (mem / 'feedback_sample.md').exists(),
           'Rejected commit leaves published edits, applied count, and successful process exit.')

with fixture() as (g, root, mem, skills, state):
    (mem / 'MEMORY.md').write_text('\n'.join('line' for _ in range(190)) + '\n')
    run_fake(g, [item()])
    record('no_index_budget_in_apply', len((mem / 'MEMORY.md').read_text().splitlines()) == 191,
           'Reflector writes and commits beyond the deployed 190-line Stop-hook threshold.')

with fixture() as (g, root, mem, skills, state):
    outside = root / 'other-project.md'; outside.write_text('other scope\n')
    (mem / 'linked.md').symlink_to(outside)
    it = item(kind='update'); it['target_file'] = 'linked.md'
    g['apply']([it], '2026-09-26', [{'brian': 'Use the blue option'}], False)
    record('update_follows_symlink', 'Update 2026-09-26' in outside.read_text(),
           'basename filtering does not prevent a memory symlink update outside the memory directory.')

with fixture() as (g, root, mem, skills, state):
    run_fake(g, [item()])
    f = mem / 'feedback_sample.md'; f.write_text(f.read_text() + 'later human change\n')
    git(mem, 'add', '.'); git(mem, 'commit', '-qm', 'later change')
    rc = g['undo'](SimpleNamespace(date='2026-09-26'))
    record('undo_conflict_exit_zero', rc == 0 and bool(git(mem, 'ls-files', '-u').stdout),
           'Conflicted revert leaves an unmerged repository but undo returns success.')

report = dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              mode='isolated CPU fixtures; no model or network; no live mutations', tests=results)
RESULT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'tests_reproduced': len(results), 'report': str(RESULT)}))
