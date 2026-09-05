# Superseded first attempt — kept as evidence, not used

These twelve generator outputs were produced under the first frozen contract
(`d97fb298…`), whose sanitizer counted only **top-level** functions named
`test_*`. The model wrote its tests inside `class Test…` blocks, which pytest
collects perfectly well, so nine of the twelve valid outputs were rejected with
"no test functions defined".

That was a defect in my detector, not a property of the outputs, and not a
policy judgement. It was found **before any bank was executed against any
historical tree**, so the correction could not have been informed by outcomes
and no output was selected, repaired or cherry-picked on the basis of results.

Per the Gen58 brief — *"any semantic contract change after first model output
=> STOP/new generation, not patch-and-continue"* — these outputs are retained
here for the record and are **not** used. The sanitizer was corrected, the
contract re-frozen at `5bad7bd7…`, and all twelve calls were regenerated from
scratch.
