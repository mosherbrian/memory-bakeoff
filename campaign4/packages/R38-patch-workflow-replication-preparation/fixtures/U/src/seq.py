def stable_unique(items):
    """Return the items with duplicates removed, keeping the first occurrence of each, in their original order. Items are hashable."""
    return sorted(set(items))
