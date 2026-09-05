import pytest
from dispatch.queue import Queue


class TestUrgentJobsPriority:
    """Tests for urgent job priority handling."""

    def test_urgent_job_pops_before_ordinary(self):
        """An urgent job added before an ordinary job should be popped first."""
        q = Queue()
        q.push("ordinary")
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"
        assert q.pop() == "ordinary"

    def test_urgent_job_pops_before_multiple_ordinary(self):
        """An urgent job should be popped before all ordinary jobs currently in queue."""
        q = Queue()
        q.push("a")
        q.push("b")
        q.push("c")
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"
        assert q.pop() == "a"
        assert q.pop() == "b"
        assert q.pop() == "c"

    def test_urgent_jobs_run_in_fifo_order_among_themselves(self):
        """Urgent jobs should maintain their insertion order relative to each other."""
        q = Queue()
        q.push("ordinary")
        q.push("urgent1", urgent=True)
        q.push("urgent2", urgent=True)
        q.push("ordinary2")
        
        assert q.pop() == "urgent1"
        assert q.pop() == "urgent2"
        assert q.pop() == "ordinary"
        assert q.pop() == "ordinary2"

    def test_multiple_urgent_jobs_interleaved_with_ordinary(self):
        """Multiple urgent jobs should all jump ahead of all ordinary jobs."""
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

    def test_urgent_job_added_first_pops_first(self):
        """If an urgent job is added first, it should be popped first."""
        q = Queue()
        q.push("urgent", urgent=True)
        q.push("ordinary")
        assert q.pop() == "urgent"
        assert q.pop() == "ordinary"

    def test_urgent_job_added_after_multiple_ordinary_pops_before_all(self):
        """An urgent job added after several ordinary jobs should still pop before them."""
        q = Queue()
        q.push("a")
        q.push("b")
        q.push("c")
        q.push("urgent", urgent=True)
        
        assert q.pop() == "urgent"
        assert q.pop() == "a"
        assert q.pop() == "b"
        assert q.pop() == "c"

    def test_only_urgent_jobs(self):
        """Queue with only urgent jobs should behave like a normal FIFO queue."""
        q = Queue()
        q.push("u1", urgent=True)
        q.push("u2", urgent=True)
        q.push("u3", urgent=True)
        
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        assert q.pop() == "u3"

    def test_only_ordinary_jobs(self):
        """Queue with only ordinary jobs should behave like a normal FIFO queue."""
        q = Queue()
        q.push("a")
        q.push("b")
        q.push("c")
        
        assert q.pop() == "a"
        assert q.pop() == "b"
        assert q.pop() == "c"

    def test_empty_queue_pop_raises(self):
        """Popping from an empty queue should raise IndexError."""
        q = Queue()
        with pytest.raises(IndexError):
            q.pop()

    def test_push_ordinary_default(self):
        """push() without urgent parameter should add an ordinary job."""
        q = Queue()
        q.push("a")
        q.push("b", urgent=False)
        assert q.pop() == "a"
        assert q.pop() == "b"

    def test_urgent_job_insertion_position(self):
        """Urgent jobs should be inserted at the front of the queue relative to ordinary jobs."""
        q = Queue()
        q.push("a")
        q.push("b")
        q.push("urgent", urgent=True)
        q.push("c")
        q.push("urgent2", urgent=True)
        
        # Order should be: urgent, urgent2, a, b, c
        assert q.pop() == "urgent"
        assert q.pop() == "urgent2"
        assert q.pop() == "a"
        assert q.pop() == "b"
        assert q.pop() == "c"

    def test_mixed_sequence_complex(self):
        """Complex mixed sequence of urgent and ordinary jobs."""
        q = Queue()
        q.push("o1")
        q.push("o2")
        q.push("u1", urgent=True)
        q.push("o3")
        q.push("u2", urgent=True)
        q.push("u3", urgent=True)
        q.push("o4")
        q.push("o5")
        
        # Urgent jobs (u1, u2, u3) should all come before ordinary jobs (o1, o2, o3, o4, o5)
        # Urgent jobs maintain their order: u1, u2, u3
        # Ordinary jobs maintain their order: o1, o2, o3, o4, o5
        assert q.pop() == "u1"
        assert q.pop() == "u2"
        assert q.pop() == "u3"
        assert q.pop() == "o1"
        assert q.pop() == "o2"
        assert q.pop() == "o3"
        assert q.pop() == "o4"
        assert q.pop() == "o5"

    def test_single_urgent_job(self):
        """A single urgent job should be popped correctly."""
        q = Queue()
        q.push("urgent", urgent=True)
        assert q.pop() == "urgent"

    def test_single_ordinary_job(self):
        """A single ordinary job should be popped correctly."""
        q = Queue()
        q.push("ordinary")
        assert q.pop() == "ordinary"
