def clamp(x, lo, hi):
    """Return x limited to the closed range [lo, hi]; lo <= hi."""
    return max(lo, min(x, hi - 1))
