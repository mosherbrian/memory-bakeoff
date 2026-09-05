import pytest
from dispatch.queue import Queue


class TestUrgentJobOrdering:
    def test_urgent_job_comes_before_ordinary(self):
        """An urgent job should run before every ordinary job currently waiting."""
        q = Queue()
        q.push("ordinary")
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"
        assert q.pop() == "ordinary"

    def test_urgent_job_comes_before_multiple_ordinary(self):
        """An urgent job should run before all ordinary jobs currently waiting."""
        q = Queue()
        q.push("a")
        q.push("b")
        q.push("c")
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"
        assert q.pop() == "a"
        assert q.pop() == "b"
        assert q.pop() == "c"

    def test_multiple_urgent_jobs_order(self):
        """Urgent jobs run among themselves in the order they were added."""
        q = Queue()
        q.push("urgent1", urgent=True)
        q.push("urgent2", urgent=True)
        assert q.pop() == "urgent1"
        assert q.pop() == "urgent2"

    def test_urgent_jobs_before_ordinary_in_mixed_sequence(self):
        """Urgent jobs should be interleaved correctly with ordinary jobs."""
        q = Queue()
        q.push("o1")
        q.push("u1", urgent=True)
        q.push("o2")
        q.push("u2", urgent=True)
        q.push("o3")
        
        # First urgent job comes before all ordinary jobs
        assert q.pop() == "u1"
        # Second urgent job comes before remaining ordinary jobs
        assert q.pop() == "u2"
        # Then ordinary jobs in order
        assert q.pop() == "o1"
        assert q.pop() == "o2"
        assert q.pop() == "o3"

    def test_urgent_job_inserted_into_empty_queue(self):
        """An urgent job added to an empty queue should be the only job."""
        q = Queue()
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"

    def test_ordinary_job_after_urgent_job(self):
        """An ordinary job added after an urgent job should come after it."""
        q = Queue()
        q.push("urgent", urgent=True)
        q.push("ordinary")
        assert q.pop() == "urgent"
        assert q.pop() == "ordinary"

    def test_urgent_job_between_ordinary_jobs(self):
        """An urgent job added between two ordinary jobs should run before both."""
        q = Queue()
        q.push("o1")
        q.push("u1", urgent=True)
        q.push("o2")
        
        assert q.pop() == "u1"
        assert q.pop() == "o1"
        assert q.pop() == "o2"

    def test_multiple_urgent_jobs_between_ordinary_jobs(self):
        """Multiple urgent jobs added between ordinary jobs should all run before them."""
        q = Queue()
        q.push("o1")
        q.push("u1", urgent=True)
        q.push("u2", urgent=True)
        q.push("o2")
        
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        assert q.pop() == "o1"
        assert q.pop() == "o2"

    def test_urgent_job_preserves_order_with_many_ordinary(self):
        """An urgent job should run before all ordinary jobs, regardless of count."""
        q = Queue()
        for i in range(10):
            q.push(f"ordinary_{i}")
        q.push("urgent", urgent=True)
        
        assert q.pop() == "urgent"
        for i in range(10):
            assert q.pop() == f"ordinary_{i}"

    def test_ordinary_job_preserves_order_with_many_urgent(self):
        """Ordinary jobs should maintain their relative order after all urgent jobs."""
        q = Queue()
        q.push("u1", urgent=True)
        q.push("u2", urgent=True)
        q.push("o1")
        q.push("o2")
        q.push("o3")
        
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        assert q.pop() == "o1"
        assert q.pop() == "o2"
        assert q.pop() == "o3"

    def test_alternating_urgent_and_ordinary(self):
        """Alternating urgent and ordinary jobs should be handled correctly."""
        q = Queue()
        q.push("o1")
        q.push("u1", urgent=True)
        q.push("o2")
        q.push("u2", urgent=True)
        q.push("o3")
        q.push("u3", urgent=True)
        q.push("o4")
        
        # All urgent jobs come first in order
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        assert q.pop() == "u3"
        # Then all ordinary jobs in order
        assert q.pop() == "o1"
        assert q.pop() == "o2"
        assert q.pop() == "o3"
        assert q.pop() == "o4"

    def test_urgent_job_default_false(self):
        """The urgent parameter defaults to False."""
        q = Queue()
        q.push("job")
        assert q.pop() == "job"

    def test_empty_queue_raises(self):
        """Popping from an empty queue should raise an IndexError."""
        q = Queue()
        with pytest.raises(IndexError):
            q.pop()

    def test_push_ordinary_does_not_affect_urgent_order(self):
        """Adding an ordinary job should not change the order of existing urgent jobs."""
        q = Queue()
        q.push("u1", urgent=True)
        q.push("u2", urgent=True)
        q.push("o1")
        
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        assert q.pop() == "o1"
