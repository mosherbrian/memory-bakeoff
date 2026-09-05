from dispatch.queue import Queue


def test_urgent_job_runs_before_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("ordinary")
    q.push("urgent", urgent=True)
    assert q.pop() == "urgent"
    assert q.pop() == "ordinary"


def test_urgent_job_added_before_ordinary_job_runs_after_ordinary_job():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("urgent", urgent=True)
    q.push("ordinary")
    assert q.pop() == "urgent"
    assert q.pop() == "ordinary"


def test_multiple_urgent_jobs_run_in_fifo_order():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push("urgent1", urgent=True)
    q.push("urgent2", urgent=True)
    q.push("urgent3", urgent=True)
    assert q.pop() == "urgent1"
    assert q.pop() == "urgent2"
    assert q.pop() == "urgent3"


def test_urgent_jobs_run_before_all_ordinary_jobs_when_mixed():
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


def test_urgent_job_added_after_ordinary_jobs_still_runs_first():
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


def test_ordinary_job_added_after_urgent_job_runs_after():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push("urgent", urgent=True)
    q.push("ordinary")
    assert q.pop() == "urgent"
    assert q.pop() == "ordinary"


def test_push_with_urgent_false_is_ordinary():
    """REQUIREMENT: push(name) adds an ordinary job. push(name, urgent=True) adds an urgent one."""
    q = Queue()
    q.push("a", urgent=False)
    q.push("b", urgent=True)
    assert q.pop() == "b"
    assert q.pop() == "a"


def test_pop_returns_correct_name():
    """REQUIREMENT: pop() removes and returns the next job to run."""
    q = Queue()
    q.push("job_name")
    result = q.pop()
    assert result == "job_name"


def test_urgent_jobs_interleave_correctly_with_ordinary():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting, and urgent jobs run among themselves in the order they were added."""
    q = Queue()
    q.push("o1")
    q.push("u1", urgent=True)
    q.push("o2")
    q.push("u2", urgent=True)
    q.push("o3")
    q.push("u3", urgent=True)
    assert q.pop() == "u1"
    assert q.pop() == "u2"
    assert q.pop() == "u3"
    assert q.pop() == "o1"
    assert q.pop() == "o2"
    assert q.pop() == "o3"
