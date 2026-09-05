import pytest
from dispatch.queue import Queue


class TestUrgentJobPrecedence:
    """Tests for urgent job priority over ordinary jobs."""

    def test_urgent_job_runs_before_ordinary_job(self):
        """An urgent job should be popped before any ordinary jobs."""
        q = Queue()
        q.push("ordinary")
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"
        assert q.pop() == "ordinary"

    def test_urgent_job_inserted_between_ordinary_jobs(self):
        """An urgent job should jump ahead of all currently waiting ordinary jobs."""
        q = Queue()
        q.push("first")
        q.push("second")
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"
        assert q.pop() == "first"
        assert q.pop() == "second"

    def test_multiple_urgent_jobs_before_ordinary_jobs(self):
        """All urgent jobs should be popped before any ordinary jobs."""
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


class TestUrgentJobOrdering:
    """Tests for FIFO ordering among urgent jobs."""

    def test_urgent_jobs_keep_fifo_order(self):
        """Urgent jobs should be popped in the order they were added."""
        q = Queue()
        q.push("u1", urgent=True)
        q.push("u2", urgent=True)
        q.push("u3", urgent=True)
        
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        assert q.pop() == "u3"

    def test_urgent_jobs_mixed_with_ordinary_keep_respective_orders(self):
        """Urgent jobs maintain their relative order, and ordinary jobs maintain theirs."""
        q = Queue()
        q.push("o1")
        q.push("u1", urgent=True)
        q.push("o2")
        q.push("u2", urgent=True)
        q.push("o3")
        
        # Urgent jobs come out first, in order
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        # Then ordinary jobs, in order
        assert q.pop() == "o1"
        assert q.pop() == "o2"
        assert q.pop() == "o3"


class TestMixedScenarios:
    """Complex scenarios mixing urgent and ordinary jobs."""

    def test_empty_queue_raises(self):
        """Popping from an empty queue should raise an error."""
        q = Queue()
        with pytest.raises(IndexError):
            q.pop()

    def test_push_without_urgent_flag_is_ordinary(self):
        """push(name) without urgent=True should be treated as ordinary."""
        q = Queue()
        q.push("a")
        q.push("b", urgent=False)
        q.push("c")
        
        assert q.pop() == "a"
        assert q.pop() == "b"
        assert q.pop() == "c"

    def test_urgent_after_ordinary_then_ordinary(self):
        """Ensure the queue state is correct after interleaved operations."""
        q = Queue()
        q.push("a")
        q.push("b", urgent=True)
        q.pop()  # Should get "b"
        q.push("c")
        
        assert q.pop() == "a"
        assert q.pop() == "c"

    def test_all_urgent_jobs(self):
        """Queue with only urgent jobs should behave like a standard FIFO queue."""
        q = Queue()
        q.push("x", urgent=True)
        q.push("y", urgent=True)
        q.push("z", urgent=True)
        
        assert q.pop() == "x"
        assert q.pop() == "y"
        assert q.pop() == "z"

    def test_all_ordinary_jobs(self):
        """Queue with only ordinary jobs should behave like a standard FIFO queue."""
        q = Queue()
        q.push("x")
        q.push("y")
        q.push("z")
        
        assert q.pop() == "x"
        assert q.pop() == "y"
        assert q.pop() == "z"

    def test_urgent_job_with_no_ordinary_jobs(self):
        """An urgent job with no ordinary jobs should just be popped normally."""
        q = Queue()
        q.push("urgent_only", urgent=True)
        assert q.pop() == "urgent_only"

    def test_ordinary_job_with_no_urgent_jobs(self):
        """An ordinary job with no urgent jobs should just be popped normally."""
        q = Queue()
        q.push("ordinary_only")
        assert q.pop() == "ordinary_only"
