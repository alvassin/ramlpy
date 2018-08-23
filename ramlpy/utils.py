import re


_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')


def snake_case(s: str) -> str:
    """ Convert given string to snake case """
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()


def topological_sort(source):
    pending = [(name, set(deps)) for name, deps in source]
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, deps = entry
            deps.difference_update(emitted)
            if deps:
                next_pending.append(entry)
            else:
                yield name
                emitted.append(name)
                next_emitted.append(name)
        if not next_emitted:
            raise ValueError(
                "cyclic or missing dependancy detected: %r" % (next_pending, )
            )
        pending = next_pending
        emitted = next_emitted
