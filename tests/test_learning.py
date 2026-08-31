from memory_bakeoff.runner import run_learning_diagnostic


def test_feedback_diagnostic_non_decreasing():
    rows=run_learning_diagnostic(epochs=4)
    vals=[r["useful_before_harmful"] for r in rows]
    assert vals[-1] >= vals[0]


def test_learning_feedback_queries_are_disjoint_from_eval_queries():
    from memory_bakeoff.corpus import learning_stream, learning_training_cases
    _, eval_cases = learning_stream()
    train_cases = learning_training_cases()
    assert {c.id for c in eval_cases}.isdisjoint({c.id for c in train_cases})
    assert [c.relevant_ids for c in eval_cases] == [c.relevant_ids for c in train_cases]
    assert [c.prohibited_ids for c in eval_cases] == [c.prohibited_ids for c in train_cases]
