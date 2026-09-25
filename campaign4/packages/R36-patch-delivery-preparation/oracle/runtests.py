"""Run every test_* function in the given test files (plain asserts or pytest style), from a repo root.
Exit 0 only if at least one test ran and all passed."""
import importlib.util, sys, traceback
sys.path.insert(0, ".")
ran = failed = 0
for path in sys.argv[1:]:
    spec = importlib.util.spec_from_file_location("t%d" % ran, path)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except Exception:
        failed += 1; traceback.print_exc(); continue
    for name in sorted(n for n in dir(m) if n.startswith("test")):
        ran += 1
        try:
            getattr(m, name)()
        except Exception:
            failed += 1; print("FAIL", path, name)
print(f"ran {ran} failed {failed}")
sys.exit(0 if ran and not failed else 1)
