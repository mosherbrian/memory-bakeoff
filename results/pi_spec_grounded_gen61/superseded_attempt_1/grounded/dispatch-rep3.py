from dispatch.queue import Queue

def test_urgent_job_runs_before_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push('ordinary')
    q.push('urgent', urgent=True)
    assert q.pop() == 'urgent'
    assert q.pop() == 'ordinary'

def test_multiple_urgent_jobs_run_in_fifo_order():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push('urgent1', urgent=True)
    q.push('urgent2', urgent=True)
    assert q.pop() == 'urgent1'
    assert q.pop() == 'urgent2'

def test_urgent_job_inserted_before_multiple_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push('o1')
    q.push('o2')
    q.push('o3')
    q.push('u1', urgent=True)
    assert q.pop() == 'u1'
    assert q.pop() == 'o1'
    assert q.pop() == 'o2'
    assert q.pop() == 'o3'

def test_all_urgent_jobs():
    """REQUIREMENT: push(name, urgent=True) adds an urgent one."""
    q = Queue()
    q.push('a', urgent=True)
    q.push('b', urgent=True)
    q.push('c', urgent=True)
    assert q.pop() == 'a'
    assert q.pop() == 'b'
    assert q.pop() == 'c'

def test_all_ordinary_jobs():
    """REQUIREMENT: push(name) adds an ordinary job."""
    q = Queue()
    q.push('a')
    q.push('b')
    q.push('c')
    assert q.pop() == 'a'
    assert q.pop() == 'b'
    assert q.pop() == 'c'

def test_urgent_job_added_after_ordinary_jobs_runs_first():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push('o1')
    q.push('o2')
    q.push('u1', urgent=True)
    q.push('o3')
    assert q.pop() == 'u1'
    assert q.pop() == 'o1'
    assert q.pop() == 'o2'
    assert q.pop() == 'o3'

def test_urgent_job_added_when_queue_empty():
    """REQUIREMENT: push(name, urgent=True) adds an urgent one."""
    q = Queue()
    q.push('u1', urgent=True)
    assert q.pop() == 'u1'

def test_ordinary_job_added_when_queue_empty():
    """REQUIREMENT: push(name) adds an ordinary job."""
    q = Queue()
    q.push('o1')
    assert q.pop() == 'o1'

def test_urgent_job_between_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting, and urgent jobs run among themselves in the order they were added."""
    q = Queue()
    q.push('o1')
    q.push('u1', urgent=True)
    q.push('o2')
    q.push('u2', urgent=True)
    q.push('o3')
    q.push('o4')
    assert q.pop() == 'u1'
    assert q.pop() == 'u2'
    assert q.pop() == 'o1'
    assert q.pop() == 'o2'
    assert q.pop() == 'o3'
    assert q.pop() == 'o4'