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


def test_urgent_job_inserted_before_existing_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("first")
    q.push("second")
    q.push("urgent", urgent=True)
    assert q.pop() == "urgent"
    assert q.pop() == "first"
    assert q.pop() == "second"


def test_multiple_urgent_jobs_before_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("ordinary1")
    q.push("ordinary2")
    q.push("urgent1", urgent=True)
    q.push("urgent2", urgent=True)
    assert q.pop() == "urgent1"
    assert q.pop() == "urgent2"
    assert q.pop() == "ordinary1"
    assert q.pop() == "ordinary2"


def test_urgent_job_after_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("a")
    q.push("b", urgent=True)
    q.push("c")
    assert q.pop() == "b"
    assert q.pop() == "a"
    assert q.pop() == "c"


def test_push_with_urgent_false_is_ordinary():
    """REQUIREMENT: push(name) adds an ordinary job"""
    q = Queue()
    q.push("a", urgent=False)
    q.push("b")
    assert q.pop() == "a"
    assert q.pop() == "b"


def test_urgent_job_between_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("first")
    q.push("urgent", urgent=True)
    q.push("second")
    assert q.pop() == "urgent"
    assert q.pop() == "first"
    assert q.pop() == "second"


def test_empty_queue_raises_error():
    """REQUIREMENT: pop() removes and returns the next job to run"""
    q = Queue()
    try:
        q.pop()
        assert False, "Expected an exception when popping from an empty queue"
    except IndexError:
        pass


def test_mixed_urgent_and_ordinary_interleaved():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push("o1")
    q.push("u1", urgent=True)
    q.push("o2")
    q.push("u2", urgent=True)
    q.push("o3")
    assert q.pop() == "u1"
    assert q.pop() == "u2"
    assert q.pop() == "o1"
    assert q.pop() == "o2"
    assert q.pop() == "o3"
