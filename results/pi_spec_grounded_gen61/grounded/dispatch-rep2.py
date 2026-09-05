from dispatch.queue import Queue

def test_urgent_job_runs_before_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push('ordinary')
    q.push('urgent', urgent=True)
    assert q.pop() == 'urgent'
    assert q.pop() == 'ordinary'

def test_urgent_job_runs_before_multiple_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting"""
    q = Queue()
    q.push('a')
    q.push('b')
    q.push('urgent', urgent=True)
    assert q.pop() == 'urgent'
    assert q.pop() == 'a'
    assert q.pop() == 'b'

def test_urgent_jobs_among_themselves_run_in_fifo_order():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push('urgent1', urgent=True)
    q.push('urgent2', urgent=True)
    assert q.pop() == 'urgent1'
    assert q.pop() == 'urgent2'

def test_urgent_jobs_interleave_correctly_with_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting, and urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push('a')
    q.push('u1', urgent=True)
    q.push('b')
    q.push('u2', urgent=True)
    assert q.pop() == 'u1'
    assert q.pop() == 'u2'
    assert q.pop() == 'a'
    assert q.pop() == 'b'

def test_ordinary_jobs_keep_order_after_urgent():
    """REQUIREMENT: Ordinary jobs run in the order they were added"""
    q = Queue()
    q.push('u', urgent=True)
    q.push('a')
    q.push('b')
    assert q.pop() == 'u'
    assert q.pop() == 'a'
    assert q.pop() == 'b'

def test_multiple_urgent_jobs_before_multiple_ordinary_jobs():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting, and urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push('u1', urgent=True)
    q.push('a')
    q.push('u2', urgent=True)
    q.push('b')
    q.push('u3', urgent=True)
    assert q.pop() == 'u1'
    assert q.pop() == 'u2'
    assert q.pop() == 'u3'
    assert q.pop() == 'a'
    assert q.pop() == 'b'

def test_push_ordinary_job_default():
    """REQUIREMENT: push(name) adds an ordinary job"""
    q = Queue()
    q.push('job')
    q.push('other')
    assert q.pop() == 'job'
    assert q.pop() == 'other'

def test_push_urgent_job_explicit():
    """REQUIREMENT: push(name, urgent=True) adds an urgent one"""
    q = Queue()
    q.push('job', urgent=True)
    q.push('other')
    assert q.pop() == 'job'
    assert q.pop() == 'other'

def test_empty_queue_raises_on_pop():
    """REQUIREMENT: pop() removes and returns the next job to run"""
    q = Queue()
    try:
        q.pop()
        assert False, 'Expected an exception when popping from empty queue'
    except IndexError:
        pass