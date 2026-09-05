from dispatch.queue import Queue

def test_urgent_jobs_run_in_order_among_themselves():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push('urgent1', urgent=True)
    q.push('urgent2', urgent=True)
    assert q.pop() == 'urgent1'
    assert q.pop() == 'urgent2'
from dispatch.queue import Queue

def test_urgent_jobs_among_themselves_run_in_fifo_order():
    """REQUIREMENT: urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push('urgent1', urgent=True)
    q.push('urgent2', urgent=True)
    assert q.pop() == 'urgent1'
    assert q.pop() == 'urgent2'
from dispatch.queue import Queue

def test_mixed_urgent_and_ordinary_order():
    """REQUIREMENT: An urgent job runs before every ordinary job currently waiting, and urgent jobs run among themselves in the order they were added"""
    q = Queue()
    q.push('o1')
    q.push('u1', urgent=True)
    q.push('o2')
    q.push('u2', urgent=True)
    assert q.pop() == 'u1'
    assert q.pop() == 'u2'
    assert q.pop() == 'o1'
    assert q.pop() == 'o2'

def test_only_ordinary_jobs():
    """REQUIREMENT: Ordinary jobs run in the order they were added"""
    q = Queue()
    q.push('a')
    q.push('b')
    q.push('c')
    assert q.pop() == 'a'
    assert q.pop() == 'b'
    assert q.pop() == 'c'