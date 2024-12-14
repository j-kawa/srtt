from more_itertools import all_equal


PREFIX_WILDCHAR = "x"


def prefix_matches(prefix: str, string: str) -> bool:
    if len(prefix) != len(string):
        return False
    for pc, sc in zip(prefix, string):
        if pc == PREFIX_WILDCHAR:
            continue
        if pc != sc:
            return False
    return True


def make_prefixes(strings: set[str], length: int) -> set[str]:
    ret = set()
    for string in strings:
        ret.add(string[:length] + (len(string) - length) * PREFIX_WILDCHAR)
    return ret


def get_prefixes(accept: set[str], other: set[str]) -> list[str]:
    assert all_equal(map(len, accept))
    assert accept

    remaining = set(accept)
    ret = []
    input_length = len(next(iter(accept)))
    for length in range(input_length // 2, input_length + 1):
        prefixes = make_prefixes(remaining, length)
        for prefix in prefixes:
            if any(prefix_matches(prefix, o) for o in other):
                continue
            ret.append(prefix)
            remaining -= {s for s in remaining if prefix_matches(prefix, s)}
        if not remaining:
            return sorted(ret)
    raise ValueError("no prefix found")
