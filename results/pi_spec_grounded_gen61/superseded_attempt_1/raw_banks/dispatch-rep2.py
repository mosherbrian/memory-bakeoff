from dispatch.queue import Queue


def test_urgent_job_runs_before_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("ordinary")
    q.push("urgent", urgent=True)
    assert q.pop() == "urgent"
    assert q.pop() == "ordinary"


def test_urgent_jobs_run_in_order_among_themselves():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push("urgent1", urgent=True)
    q.push("urgent2", urgent=True)
    assert q.pop() == "urgent1"
    assert q.pop() == "urgent2"


def test_urgent_job_inserted_before_multiple_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("a")
    q.push("b")
    q.push("c")
    q.push("urgent", urgent=True)
    assert q.pop() == "urgent"
    assert q.pop() == "a"
    assert q.pop() == "b"
    assert q.pop() == "c"


def test_mixed_urgent_and_ordinary_jobs_ordering():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("a")
    q.push("urgent1", urgent=True)
    q.push("b")
    q.push("urgent2", urgent=True)
    assert q.pop() == "urgent1"
    assert q.pop() == "urgent2"
    assert q.pop() == "a"
    assert q.pop() == "b"


def test_urgent_job_added_before_any_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("urgent", urgent=True)
    q.push("ordinary")
    assert q.pop() == "urgent"
    assert q.pop() == "ordinary"


def test_multiple_urgent_jobs_inserted_between_ordinary_jobs():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push("a")
    q.push("urgent1", urgent=True)
    q.push("b")
    q.push("urgent2", urgent=True)
    q.push("c")
    assert q.pop() == "urgent1"
    assert q.pop() == "urgent2"
    assert q.pop() == "a"
    assert q.pop() == "b"
    assert q.pop() == "c"


def test_empty_queue_pop_raises_index_error():
    """REQUIREMENT: pop() removes and returns the next job to run"""
    q = Queue()
    try:
        q.pop()
        assert False, "Expected IndexError"
    except IndexError:
        pass


def test_push_with_urgent_false_is_ordinary():
    """REQUIREMENT: push(name) adds an ordinary job"""
    q = Queue()
    q.push("a")
    q.push("b", urgent=False)
    assert q.pop() == "a"
    assert q.pop() == "b"


def test_urgent_job_after_ordinary_jobs_still_runs_first():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("a")
    q.push("b")
    q.push("urgent", urgent=True)
    q.push("c")
    assert q.pop() == "urgent"
    assert q.pop() == "a"
    assert q.pop() == "b"
    assert q.pop() == "c"
