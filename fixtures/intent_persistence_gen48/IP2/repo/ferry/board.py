from ferry.schedule import as_list


def render() -> str:
    return " | ".join(as_list())
