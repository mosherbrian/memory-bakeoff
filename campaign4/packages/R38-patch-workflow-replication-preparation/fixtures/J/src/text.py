def join_nonempty(parts, sep=","):
    """Join the parts with sep, converting each to str and skipping only None and the empty string."""
    return sep.join(str(p) for p in parts if p)
