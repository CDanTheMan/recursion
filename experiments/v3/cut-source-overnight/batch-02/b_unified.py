"""Unified positional-state implementation of the paired collection alternatives."""


def step(state, action, n):
    clock, offered, stamps, one, drain, two = state
    clock += 1
    stamps = list(stamps)
    if action == "O" and offered < n:
        stamps[offered] = clock
        offered += 1
    policies = []
    for kind, old in enumerate((one, drain, two)):
        v, cap, pos, active, checked, retry, reads, captures, checks, invalid, retries, postponed, waits, budget = old
        reads, waits = list(reads), list(waits)
        if action == "A" and v < offered:
            if active:
                postponed += 1
            else:
                waits[v] = clock - stamps[v]
                v += 1
                budget = max(0, budget - 1)
        elif action == "C":
            if not active:
                if checked != v and (kind == 0 or v == offered or (kind == 2 and budget == 0)):
                    cap, pos, active = v, 0, True
                    captures += 1
                    budget = 0
                    retries += int(retry)
                    retry = False
            elif pos < cap:
                reads[pos] += 1
                pos += 1
            else:
                checks += 1
                active = False
                budget = 2
                if cap == v:
                    checked = cap
                else:
                    invalid += 1
                    retry = True
        policies.append((v, cap, pos, active, checked, retry, tuple(reads), captures,
                         checks, invalid, retries, postponed, tuple(waits), budget))
    return (clock, offered, tuple(stamps), *policies)
