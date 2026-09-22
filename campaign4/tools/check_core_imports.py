#!/usr/bin/env python3
"""Static dependency gate. Usage: python3 check_core_imports.py CORE_SRC.
Does not import/execute the core. Dynamic import names require explicit review.
This checks dependencies, not portability of subprocesses, paths or OS behavior.
"""
import ast
from pathlib import Path
import sys


def check(root):
    root = root.resolve()
    files = sorted(root.rglob('*.py'))
    if not files:
        return ['no Python source files found']
    own = {p.stem for p in root.glob('*.py')}
    own |= {p.name for p in root.iterdir() if p.is_dir() and (p / '__init__.py').is_file()}
    allowed = set(sys.stdlib_module_names) | own
    errors = []
    for path in files:
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f'{path}: cannot parse: {exc}')
            continue
        dynamic = {'__import__'}
        importlib_aliases = {'importlib'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                importlib_aliases |= {a.asname or a.name for a in node.names if a.name == 'importlib'}
            if isinstance(node, ast.ImportFrom) and node.module in ('importlib', 'builtins'):
                dynamic |= {a.asname or a.name for a in node.names if a.name in ('import_module', '__import__')}
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = path.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    if not base.is_relative_to(root):
                        errors.append(f'{path}:{node.lineno}: relative import escapes core')
                    continue
                names = [node.module or '']
            elif isinstance(node, ast.Call):
                f = node.func
                is_dynamic = (isinstance(f, ast.Name) and f.id in dynamic) or (
                    isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                    and f.value.id in importlib_aliases and f.attr == 'import_module')
                if not is_dynamic:
                    continue
                if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                    errors.append(f'{path}:{node.lineno}: dynamic import needs explicit review')
                    continue
                names = [node.args[0].value]
            for name in names:
                if name.split('.')[0] not in allowed:
                    errors.append(f'{path}:{node.lineno}: forbidden dependency {name!r}')
    return errors


if __name__ == '__main__':
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit('usage: check_core_imports.py CORE_SRC_DIRECTORY')
    issues = check(Path(sys.argv[1]))
    print('\n'.join(issues) if issues else 'PASS: static core imports are stdlib or core-owned')
    sys.exit(bool(issues))
