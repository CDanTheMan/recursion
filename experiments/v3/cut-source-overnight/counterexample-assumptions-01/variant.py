"""Declared semantic variant: allow only sealed collection to reopen an unchanged count."""


def step(state, action, n):
    clock, offered, stamps, optimistic, sealed = state
    clock += 1
    stamps = list(stamps)
    if action == "O" and offered < n:
        stamps[offered] = clock
        offered += 1
    policies = []
    for locking, old in ((False, optimistic), (True, sealed)):
        v, cap, pos, active, checked, retry, reads, captures, checks, invalid, retries, postponed, waits = old
        reads, waits = list(reads), list(waits)
        if action == "A" and v < offered:
            if locking and active:
                postponed += 1
            else:
                waits[v] = clock - stamps[v]
                v += 1
        elif action == "C":
            if not active:
                if checked != v or locking:
                    cap, pos, active = v, 0, True
                    captures += 1
                    retries += int(retry)
                    retry = False
            elif pos < cap:
                reads[pos] += 1
                pos += 1
            else:
                checks += 1
                active = False
                if cap == v:
                    checked = cap
                else:
                    invalid += 1
                    retry = True
        policies.append((v, cap, pos, active, checked, retry, tuple(reads), captures,
                         checks, invalid, retries, postponed, tuple(waits)))
    return (clock, offered, tuple(stamps), *policies)
