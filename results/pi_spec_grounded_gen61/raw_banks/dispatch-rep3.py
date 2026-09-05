from dispatch.queue import Queue


def test_urgent_job_precedes_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("ordinary")
    q.push("urgent", urgent=True)
    assert q.pop() == "urgent"
    assert q.pop() == "ordinary"


def test_urgent_jobs_run_in_fifo_order_among_themselves():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push("urgent1", urgent=True)
    q.push("urgent2", urgent=True)
    assert q.pop() == "urgent1"
    assert q.pop() == "urgent2"


def test_mixed_urgent_and_ordinary_order():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting, and urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push("o1")
    q.push("u1", urgent=True)
    q.push("o2")
    q.push("u2", urgent=True)
    assert q.pop() == "u1"
    assert q.pop() == "u2"
    assert q.pop() == "o1"
    assert q.pop() == "o2"


def test_multiple_urgent_jobs_inserted_between_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
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


def test_urgent_job_when_queue_empty():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("u1", urgent=True)
    assert q.pop() == "u1"


def test_only_ordinary_jobs():
    """REQUIREMENT: Ordinary jobs run in the order they were added"""
    q = Queue()
    q.push("a")
    q.push("b")
    q.push("c")
    assert q.pop() == "a"
    assert q.pop() == "b"
    assert q.pop() == "c"


def test_only_urgent_jobs():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push("u1", urgent=True)
    q.push("u2", urgent=True)
    q.push("u3", urgent=True)
    assert q.pop() == "u1"
    assert q.pop() == "u2"
    assert q.pop() == "u3"


def test_urgent_job_added_after_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("o1")
    q.push("o2")
    q.push("u1", urgent=True)
    assert q.pop() == "u1"
    assert q.pop() == "o1"
    assert q.pop() == "o2"


def test_ordinary_job_added_after_urgent_jobs():
    """REQUIREMENT: Ordinary jobs run in the order they were added"""
    q = Queue()
    q.push("u1", urgent=True)
    q.push("o1")
    q.push("o2")
    assert q.pop() == "u1"
    assert q.pop() == "o1"
    assert q.pop() == "o2"
