from dispatch.queue import Queue


def test_single_job_comes_back():
    q = Queue()
    q.push("a")
    assert q.pop() == "a"


def test_ordinary_jobs_keep_their_order():
    q = Queue()
    q.push("a")
    q.push("b")
    assert q.pop() == "a"
    assert q.pop() == "b"
